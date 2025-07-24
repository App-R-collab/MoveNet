import math
from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuario personalizado (puedes ajustar campos según tu proyecto)
class CustomUser(AbstractUser):
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    def __str__(self):
        return self.username

class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    car_plate = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Conductor: {self.user.username}"

class Passenger(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pasajero: {self.user.username}"

class Trip(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('assigned', 'Asignado'),
        ('in_progress', 'En curso'),
        ('completed', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    ]

    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    origin_lat = models.FloatField()
    origin_lng = models.FloatField()
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()
    fare = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Viaje {self.id} - Pasajero: {self.passenger.user.username} - Estado: {self.status}"

    def save(self, *args, **kwargs):
        # Parámetros de tarifa
        TARIFA_BASE = 3000  # Tarifa base en tu moneda local
        PRECIO_POR_KM = 1200  # Precio por kilómetro

        # Calcular distancia usando la fórmula de Haversine
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Radio de la Tierra en km
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c

        # Solo calcular si hay coordenadas válidas
        if self.origin_lat and self.origin_lng and self.destination_lat and self.destination_lng:
            distancia_km = haversine(self.origin_lat, self.origin_lng, self.destination_lat, self.destination_lng)
            self.fare = round(TARIFA_BASE + (distancia_km * PRECIO_POR_KM), 2)
        else:
            self.fare = None

        super().save(*args, **kwargs)