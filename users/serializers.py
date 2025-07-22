from rest_framework import serializers
from .models import Trip, Passenger, Driver

class TripSerializer(serializers.ModelSerializer):
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Trip
        fields = [
            'id',
            'passenger',
            'driver',
            'origin_lat',
            'origin_lng',
            'destination_lat',
            'destination_lng',
            'fare',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']