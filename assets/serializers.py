from rest_framework import serializers
from assets.models import ProductType, Depot, Tank, PipelineSegment


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'tenant', 'name', 'color_code', 'specific_gravity',
                  'max_interface_mixing_tolerance']
        read_only_fields = ['id']


class DepotSerializer(serializers.ModelSerializer):
    tank_count = serializers.IntegerField(source='tanks.count', read_only=True)

    class Meta:
        model = Depot
        fields = ['id', 'tenant', 'name', 'latitude', 'longitude', 'tank_count']
        read_only_fields = ['id']


class TankSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    product_name = serializers.CharField(source='product_type.name', read_only=True)
    product_color = serializers.CharField(source='product_type.color_code', read_only=True)
    ullage = serializers.FloatField(read_only=True)
    fill_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Tank
        fields = ['id', 'depot', 'depot_name', 'name', 'product_type', 'product_name',
                  'product_color', 'max_capacity', 'safe_fill_capacity',
                  'current_volume', 'current_temperature', 'status',
                  'ullage', 'fill_percentage', 'updated_at']
        read_only_fields = ['id', 'ullage', 'fill_percentage', 'updated_at']


class TankTelemetryUpdateSerializer(serializers.Serializer):
    """Serializer for external systems pushing tank telemetry data."""
    tank_id = serializers.IntegerField()
    current_volume = serializers.FloatField()
    current_temperature = serializers.FloatField(required=False)
    product_type_name = serializers.CharField(required=False)


class PipelineSegmentSerializer(serializers.ModelSerializer):
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)

    class Meta:
        model = PipelineSegment
        fields = ['id', 'tenant', 'name', 'origin', 'origin_name',
                  'destination', 'destination_name', 'length_km',
                  'diameter_inches', 'volume_capacity', 'status',
                  'current_flow_rate', 'current_pressure',
                  'geojson_path', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class PipelineScadaUpdateSerializer(serializers.Serializer):
    """Serializer for SCADA systems pushing pipeline segment data."""
    segment_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=['FLOWING', 'STATIC', 'OFFLINE', 'PIGGING', 'MAINTENANCE']
    )
    flow_rate = serializers.FloatField(required=False)
    pressure = serializers.FloatField(required=False)
