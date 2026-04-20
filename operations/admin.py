from django.contrib import admin
from operations.models import Batch, BatchHistory, VesselDischarge


class BatchHistoryInline(admin.TabularInline):
    model = BatchHistory
    extra = 0
    readonly_fields = ('recorded_at', 'position_km', 'temperature',
                       'pressure', 'interface_mixing_volume')


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_identifier', 'product_type', 'segment', 'status',
                    'current_position_km', 'start_time', 'estimated_arrival_time')
    list_filter = ('status', 'product_type')
    search_fields = ('batch_identifier',)
    inlines = [BatchHistoryInline]


@admin.register(VesselDischarge)
class VesselDischargeAdmin(admin.ModelAdmin):
    list_display = ('vessel_name', 'tenant', 'terminal_depot', 'product_type',
                    'total_volume', 'discharged_volume', 'status')
    list_filter = ('status', 'tenant')
    search_fields = ('vessel_name',)
