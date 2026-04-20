from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from core.forms import TankForm, PipelineSegmentForm
import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tenant, User
from assets.models import ProductType, Depot, Tank, PipelineSegment
from assets.serializers import (
    ProductTypeSerializer, DepotSerializer, TankSerializer,
    PipelineSegmentSerializer, TankTelemetryUpdateSerializer,
    PipelineScadaUpdateSerializer,
)
from core.permissions import IsTenantUser, TenantQuerysetMixin
from telemetry.models import ApiIngestionLog

logger = logging.getLogger('pipeline')


class ProductTypeViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [IsTenantUser]
    filterset_fields = ['name']


class DepotViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Depot.objects.prefetch_related('tanks').all()
    serializer_class = DepotSerializer
    permission_classes = [IsTenantUser]
    search_fields = ['name']


class TankViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Tank.objects.select_related('depot', 'product_type').all()
    serializer_class = TankSerializer
    permission_classes = [IsTenantUser]
    tenant_field = 'depot__tenant'
    filterset_fields = ['depot', 'product_type', 'status']
    search_fields = ['name']
    ordering_fields = ['current_volume', 'updated_at']

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest_telemetry(self, request):
        """
        POST /api/assets/tanks/ingest/
        Accept bulk tank telemetry updates from external systems.
        Payload: [{ tank_id, current_volume, current_temperature, product_type_name }]
        """
        tenant = request.tenant
        data = request.data if isinstance(request.data, list) else [request.data]
        errors = []
        updated = 0

        for item in data:
            ser = TankTelemetryUpdateSerializer(data=item)
            if not ser.is_valid():
                errors.append({'data': item, 'errors': ser.errors})
                continue

            try:
                tank = Tank.objects.select_related('depot').get(
                    pk=ser.validated_data['tank_id'],
                    depot__tenant=tenant,
                )
            except Tank.DoesNotExist:
                errors.append({'data': item, 'errors': 'Tank not found for this tenant.'})
                continue

            tank.current_volume = ser.validated_data['current_volume']
            if 'current_temperature' in ser.validated_data:
                tank.current_temperature = ser.validated_data['current_temperature']
            tank.save(update_fields=['current_volume', 'current_temperature', 'updated_at'])
            updated += 1

        # Audit log
        ApiIngestionLog.objects.create(
            tenant=tenant,
            source_system='tank_telemetry',
            endpoint='/api/assets/tanks/ingest/',
            payload=request.data,
            ip_address=request.META.get('REMOTE_ADDR'),
            status_code=200 if not errors else 207,
            error_message=str(errors) if errors else None,
        )

        return Response(
            {'updated': updated, 'errors': errors},
            status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS,
        )


class PipelineSegmentViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = PipelineSegment.objects.select_related('origin', 'destination').all()
    serializer_class = PipelineSegmentSerializer
    permission_classes = [IsTenantUser]
    filterset_fields = ['status', 'origin', 'destination']
    search_fields = ['name']

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest_scada(self, request):
        """
        POST /api/assets/segments/ingest/
        Accept pipeline SCADA updates from external systems.
        Payload: [{ segment_id, status, flow_rate, pressure }]
        """
        tenant = request.tenant
        data = request.data if isinstance(request.data, list) else [request.data]
        errors = []
        updated = 0

        for item in data:
            ser = PipelineScadaUpdateSerializer(data=item)
            if not ser.is_valid():
                errors.append({'data': item, 'errors': ser.errors})
                continue

            try:
                segment = PipelineSegment.objects.get(
                    pk=ser.validated_data['segment_id'],
                    tenant=tenant,
                )
            except PipelineSegment.DoesNotExist:
                errors.append({'data': item, 'errors': 'Segment not found for this tenant.'})
                continue

            segment.status = ser.validated_data['status']
            update_fields = ['status', 'updated_at']
            if ser.validated_data.get('flow_rate') is not None:
                segment.current_flow_rate = ser.validated_data['flow_rate']
                update_fields.append('current_flow_rate')
            if ser.validated_data.get('pressure') is not None:
                segment.current_pressure = ser.validated_data['pressure']
                update_fields.append('current_pressure')
            segment.save(update_fields=update_fields)
            
            # Create Telemetry Snapshot
            from telemetry.models import SegmentTelemetry
            design_capacity = 5000.0 # BPH - Assume a default or add to model
            util = (segment.current_flow_rate / design_capacity) * 100 if design_capacity > 0 else 0
            
            SegmentTelemetry.objects.create(
                segment=segment,
                flow_rate=segment.current_flow_rate,
                daily_volume=segment.current_flow_rate * 0.1, # Dummy incremental volume for demo
                capacity_utilization=min(100, util),
                operating_pressure=segment.current_pressure,
            )
            updated += 1

        ApiIngestionLog.objects.create(
            tenant=tenant,
            source_system='pipeline_scada',
            endpoint='/api/assets/segments/ingest/',
            payload=request.data,
            ip_address=request.META.get('REMOTE_ADDR'),
            status_code=200 if not errors else 207,
            error_message=str(errors) if errors else None,
        )

        return Response(
            {'updated': updated, 'errors': errors},
            status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS,
        )

# Template Views
class TankListView(LoginRequiredMixin, ListView):
    model = Tank
    template_name = 'assets/tank_list.html'
    context_object_name = 'tanks'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        
        if tenant:
            qs = Tank.objects.filter(depot__tenant=tenant)
        elif user.is_superuser:
            qs = Tank.objects.all()
        else:
            qs = Tank.objects.none()
            
        print(f"DEBUG: TankListView user={user}, tenant={tenant}, count={qs.count()}")
        return qs.select_related('depot', 'product_type')


class PipelineListView(LoginRequiredMixin, ListView):
    model = PipelineSegment
    template_name = 'assets/pipeline_list.html'
    context_object_name = 'segments'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        
        if tenant:
            qs = PipelineSegment.objects.filter(tenant=tenant)
        elif user.is_superuser:
            qs = PipelineSegment.objects.all()
        else:
            qs = PipelineSegment.objects.none()
            
        print(f"DEBUG: PipelineListView user={user}, tenant={tenant}, count={qs.count()}")
        return qs.select_related('origin', 'destination')


class TankCreateView(LoginRequiredMixin, CreateView):
    model = Tank
    form_class = TankForm
    template_name = 'assets/tank_form.html'
    success_url = reverse_lazy('tank_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs


class PipelineCreateView(LoginRequiredMixin, CreateView):
    model = PipelineSegment
    form_class = PipelineSegmentForm
    template_name = 'assets/pipeline_form.html'
    success_url = reverse_lazy('pipeline_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        tenant = self.request.tenant
        if not tenant and self.request.user.is_superuser:
            tenant = Tenant.objects.first()
        
        if not tenant:
            from django.core.exceptions import ValidationError
            form.add_error(None, "Could not determine tenant for this asset. Please ensure your user is linked to a tenant.")
            return self.form_invalid(form)
            
        form.instance.tenant = tenant
        return super().form_valid(form)

class TankDetailView(LoginRequiredMixin, DetailView):
    model = Tank
    template_name = 'assets/tank_detail.html'
    context_object_name = 'tank'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        if tenant:
            return Tank.objects.filter(depot__tenant=tenant)
        elif user.is_superuser:
            return Tank.objects.all()
        return Tank.objects.none()


class PipelineDetailView(LoginRequiredMixin, DetailView):
    model = PipelineSegment
    template_name = 'assets/pipeline_detail.html'
    context_object_name = 'segment'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        if tenant:
            return PipelineSegment.objects.filter(tenant=tenant)
        elif user.is_superuser:
            return PipelineSegment.objects.all()
        return PipelineSegment.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batches'] = self.object.active_batches.all()
        
        telemetry = list(self.object.telemetry.all().order_by('timestamp')[:48]) # Last 48 points
        
        import json
        context['chart_labels'] = json.dumps([t.timestamp.strftime('%H:%M') for t in telemetry])
        context['chart_data'] = json.dumps([t.daily_volume for t in telemetry])
        
        latest = telemetry[-1] if telemetry else None
        context['current_utilization'] = latest.capacity_utilization if latest else 0
        context['current_flow'] = latest.flow_rate if latest else 0
        
        return context
