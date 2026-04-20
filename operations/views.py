from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from core.forms import BatchForm
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsTenantUser, TenantQuerysetMixin
from operations.models import Batch, BatchHistory, VesselDischarge
from operations.serializers import (
    BatchSerializer, BatchHistorySerializer, BatchUpdateSerializer,
    VesselDischargeSerializer, VesselDischargeUpdateSerializer,
)
from telemetry.models import ApiIngestionLog

logger = logging.getLogger('pipeline')


class BatchViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Batch.objects.select_related(
        'segment', 'product_type', 'origin_depot', 'destination_depot'
    ).all()
    serializer_class = BatchSerializer
    permission_classes = [IsTenantUser]
    tenant_field = 'segment__tenant'
    filterset_fields = ['status', 'segment', 'product_type']
    search_fields = ['batch_identifier']
    ordering_fields = ['start_time', 'estimated_arrival_time']

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest_batch_update(self, request):
        """
        POST /api/operations/batches/ingest/
        Accept batch position / status updates from SCADA.
        Payload: [{ batch_identifier, current_position_km, status, temperature, pressure, interface_mixing_volume }]
        """
        tenant = request.tenant
        data = request.data if isinstance(request.data, list) else [request.data]
        errors = []
        updated = 0

        for item in data:
            ser = BatchUpdateSerializer(data=item)
            if not ser.is_valid():
                errors.append({'data': item, 'errors': ser.errors})
                continue

            try:
                batch = Batch.objects.get(
                    batch_identifier=ser.validated_data['batch_identifier'],
                    segment__tenant=tenant,
                )
            except Batch.DoesNotExist:
                errors.append({'data': item, 'errors': 'Batch not found for this tenant.'})
                continue

            vd = ser.validated_data
            update_fields = []

            if vd.get('current_position_km') is not None:
                batch.current_position_km = vd['current_position_km']
                update_fields.append('current_position_km')
            if vd.get('status'):
                batch.status = vd['status']
                update_fields.append('status')
            if update_fields:
                batch.save(update_fields=update_fields)

            # Record history snapshot
            BatchHistory.objects.create(
                batch=batch,
                position_km=batch.current_position_km,
                flow_rate=vd.get('flow_rate'),
                accumulated_volume=vd.get('accumulated_volume', 0.0),
                temperature=vd.get('temperature'),
                pressure=vd.get('pressure'),
                interface_mixing_volume=vd.get('interface_mixing_volume', 0.0),
            )
            updated += 1

        ApiIngestionLog.objects.create(
            tenant=tenant,
            source_system='batch_scada',
            endpoint='/api/operations/batches/ingest/',
            payload=request.data,
            ip_address=request.META.get('REMOTE_ADDR'),
            status_code=200 if not errors else 207,
            error_message=str(errors) if errors else None,
        )

        return Response(
            {'updated': updated, 'errors': errors},
            status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS,
        )


class BatchHistoryViewSet(TenantQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BatchHistory.objects.select_related('batch').all()
    serializer_class = BatchHistorySerializer
    permission_classes = [IsTenantUser]
    tenant_field = 'batch__segment__tenant'
    filterset_fields = ['batch']
    ordering_fields = ['recorded_at']


class VesselDischargeViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = VesselDischarge.objects.select_related(
        'terminal_depot', 'product_type'
    ).all()
    serializer_class = VesselDischargeSerializer
    permission_classes = [IsTenantUser]
    filterset_fields = ['status', 'terminal_depot', 'product_type']
    search_fields = ['vessel_name']

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest_discharge_update(self, request):
        """
        POST /api/operations/vessels/ingest/
        Accept discharge progress updates from terminal systems.
        Payload: [{ vessel_discharge_id, discharged_volume, status }]
        """
        tenant = request.tenant
        data = request.data if isinstance(request.data, list) else [request.data]
        errors = []
        updated = 0

        for item in data:
            ser = VesselDischargeUpdateSerializer(data=item)
            if not ser.is_valid():
                errors.append({'data': item, 'errors': ser.errors})
                continue

            try:
                vd_obj = VesselDischarge.objects.get(
                    pk=ser.validated_data['vessel_discharge_id'],
                    tenant=tenant,
                )
            except VesselDischarge.DoesNotExist:
                errors.append({'data': item, 'errors': 'VesselDischarge not found.'})
                continue

            vd_data = ser.validated_data
            vd_obj.discharged_volume = vd_data['discharged_volume']
            update_fields = ['discharged_volume']
            if vd_data.get('status'):
                vd_obj.status = vd_data['status']
                update_fields.append('status')
            vd_obj.save(update_fields=update_fields)
            updated += 1

        ApiIngestionLog.objects.create(
            tenant=tenant,
            source_system='vessel_discharge',
            endpoint='/api/operations/vessels/ingest/',
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
class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'operations/batch_list.html'
    context_object_name = 'batches'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        
        if tenant:
            qs = Batch.objects.filter(segment__tenant=tenant)
        elif user.is_superuser:
            qs = Batch.objects.all()
        else:
            qs = Batch.objects.none()
            
        print(f"DEBUG: BatchListView user={user}, tenant={tenant}, count={qs.count()}")
        return qs.select_related('segment', 'product_type', 'origin_depot', 'destination_depot')


class VesselListView(LoginRequiredMixin, ListView):
    model = VesselDischarge
    template_name = 'operations/vessel_list.html'
    context_object_name = 'vessels'

    def get_queryset(self):
        return VesselDischarge.objects.filter(tenant=self.request.tenant).select_related(
            'terminal_depot', 'product_type'
        )

class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'operations/batch_form.html'
    success_url = reverse_lazy('batch_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

class BatchDetailView(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = 'operations/batch_detail.html'
    context_object_name = 'batch'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        if tenant:
            return Batch.objects.filter(segment__tenant=tenant)
        elif user.is_superuser:
            return Batch.objects.all()
        return Batch.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history = self.object.history.all().order_by('recorded_at')
        context['history'] = history.order_by('-recorded_at')[:20]
        context['remaining_km'] = max(0, self.object.segment.length_km - self.object.current_position_km)
        
        # Prepare data for Chart.js
        import json
        chart_points = history.order_by('recorded_at')
        context['chart_labels'] = json.dumps([p.recorded_at.strftime('%H:%M') for p in chart_points])
        context['chart_data'] = json.dumps([p.flow_rate or 0 for p in chart_points])
        
        return context
