from django.contrib import admin
from assets.models import ProductType, Depot, Tank, PipelineSegment


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'color_code', 'specific_gravity')
    list_filter = ('tenant',)


@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'latitude', 'longitude')
    list_filter = ('tenant',)
    search_fields = ('name',)


class TankInline(admin.TabularInline):
    model = Tank
    extra = 0
    readonly_fields = ('current_volume', 'current_temperature', 'updated_at')


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('name', 'depot', 'product_type', 'current_volume',
                    'safe_fill_capacity', 'status', 'updated_at')
    list_filter = ('status', 'depot', 'product_type')
    search_fields = ('name',)


@admin.register(PipelineSegment)
class PipelineSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'origin', 'destination', 'status',
                    'current_flow_rate', 'current_pressure', 'updated_at')
    list_filter = ('status', 'tenant')
    search_fields = ('name',)
