from rest_framework import serializers
from .models import Trip, Passenger, Driver

class TripSerializer(serializers.ModelSerializer):
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), allow_null=True, required=False)
    passenger_username = serializers.SerializerMethodField(read_only=True)
    driver_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id',
            'passenger',
            'passenger_username',
            'driver',
            'driver_username',
            'origin_lat',
            'origin_lng',
            'destination_lat',
            'destination_lng',
            'fare',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'passenger_username', 'driver_username']

    def get_passenger_username(self, obj):
        return obj.passenger.user.username if obj.passenger and obj.passenger.user else None

    def get_driver_username(self, obj):
        return obj.driver.user.username if obj.driver and obj.driver.user else None

class DriverLocationUpdateSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class TripStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['status']

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Trip.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("Estado inválido.")
        return value    