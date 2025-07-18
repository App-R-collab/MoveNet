from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuario extendido
class CustomUser(AbstractUser):
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    def __str__(self):
        return self.username

# Modelo de Conductor
class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=20)
    car_plate = models.CharField(max_length=10)
    is_approved = models.BooleanField(default=False)  # Se aprueba manualmente
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conductor: {self.user.username}"

# Modelo de Pasajero
class Passenger(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Pasajero: {self.user.username}"
