from rest_framework import serializers
from operations.models import Batch, BatchHistory, VesselDischarge


class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_type.name', read_only=True)
    product_color = serializers.CharField(source='product_type.color_code', read_only=True)
    segment_name = serializers.CharField(source='segment.name', read_only=True)
    origin_name = serializers.CharField(source='origin_depot.name', read_only=True)
    destination_name = serializers.CharField(source='destination_depot.name', read_only=True)

    class Meta:
        model = Batch
        fields = ['id', 'batch_identifier', 'segment', 'segment_name',
                  'product_type', 'product_name', 'product_color',
                  'total_volume', 'origin_depot', 'origin_name',
                  'destination_depot', 'destination_name',
                  'start_time', 'estimated_arrival_time',
                  'current_position_km', 'status']
        read_only_fields = ['id']


class BatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchHistory
        fields = ['id', 'batch', 'recorded_at', 'position_km', 'flow_rate', 'accumulated_volume',
                  'temperature', 'pressure', 'interface_mixing_volume']
        read_only_fields = ['id', 'recorded_at']


class BatchUpdateSerializer(serializers.Serializer):
    """For SCADA to push batch position / status updates."""
    batch_identifier = serializers.CharField()
    current_position_km = serializers.FloatField(required=False)
    status = serializers.ChoiceField(
        choices=['SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED'],
        required=False,
    )
    temperature = serializers.FloatField(required=False)
    pressure = serializers.FloatField(required=False)
    flow_rate = serializers.FloatField(required=False)
    accumulated_volume = serializers.FloatField(required=False)
    interface_mixing_volume = serializers.FloatField(required=False, default=0.0)


class VesselDischargeSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_type.name', read_only=True)
    terminal_name = serializers.CharField(source='terminal_depot.name', read_only=True)
    remaining_volume = serializers.FloatField(read_only=True)

    class Meta:
        model = VesselDischarge
        fields = ['id', 'tenant', 'vessel_name', 'terminal_depot', 'terminal_name',
                  'product_type', 'product_name', 'total_volume',
                  'discharged_volume', 'remaining_volume',
                  'start_time', 'estimated_completion_time', 'status']
        read_only_fields = ['id', 'remaining_volume']


class VesselDischargeUpdateSerializer(serializers.Serializer):
    """For terminal systems pushing discharge progress."""
    vessel_discharge_id = serializers.IntegerField()
    discharged_volume = serializers.FloatField()
    status = serializers.ChoiceField(
        choices=['SCHEDULED', 'BERTHED', 'DISCHARGING', 'COMPLETED'],
        required=False,
    )
