from django import forms
from assets.models import Tank, PipelineSegment, Depot, ProductType
from operations.models import Batch
from core.models import Tenant


class TankForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['depot'].queryset = Depot.objects.filter(tenant=tenant)
            self.fields['product_type'].queryset = ProductType.objects.filter(tenant=tenant)

    class Meta:
        model = Tank
        fields = ['depot', 'name', 'product_type', 'max_capacity', 'safe_fill_capacity', 'status']
        widgets = {
            'depot': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl', 'placeholder': 'e.g. TK-101'}),
            'product_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'safe_fill_capacity': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
        }


class PipelineSegmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['origin'].queryset = Depot.objects.filter(tenant=tenant)
            self.fields['destination'].queryset = Depot.objects.filter(tenant=tenant)

    class Meta:
        model = PipelineSegment
        fields = ['name', 'origin', 'destination', 'length_km', 'diameter_inches', 'volume_capacity', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'origin': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'destination': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'length_km': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'diameter_inches': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'volume_capacity': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
        }


class BatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['segment'].queryset = PipelineSegment.objects.filter(tenant=tenant)
            self.fields['product_type'].queryset = ProductType.objects.filter(tenant=tenant)
            self.fields['origin_depot'].queryset = Depot.objects.filter(tenant=tenant)
            self.fields['destination_depot'].queryset = Depot.objects.filter(tenant=tenant)

    class Meta:
        model = Batch
        fields = ['batch_identifier', 'segment', 'product_type', 'total_volume', 'origin_depot', 'destination_depot', 'start_time', 'estimated_arrival_time', 'status']
        widgets = {
            'batch_identifier': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl', 'placeholder': 'e.g. BATCH-2026-X'}),
            'segment': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'product_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'total_volume': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'origin_depot': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'destination_depot': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl', 'type': 'datetime-local'}),
            'estimated_arrival_time': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
        }


class TenantBrandingForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'primary_color', 'secondary_color', 'logo', 'favicon', 'login_background']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'primary_color': forms.TextInput(attrs={'class': 'w-full px-1 py-1 border rounded-xl h-12', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'w-full px-1 py-1 border rounded-xl h-12', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl'}),
            'favicon': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl'}),
            'login_background': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-xl'}),
        }

from alerts.models import AlertRule

class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = ['name', 'entity_type', 'metric', 'condition', 'threshold', 'message_template', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'entity_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'metric': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl', 'placeholder': 'e.g. pressure'}),
            'condition': forms.Select(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'threshold': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'message_template': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-primary rounded'}),
        }
