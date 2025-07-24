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

# Modelo para gestionar reportes
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('incidente', 'Incidente'),
        ('sospecha', 'Sospecha'),
        ('otro', 'Otro'),
    ]

    STATUS_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_seguimiento', 'En seguimiento'),
        ('llamada_conductor', 'Llamada al conductor'),
        ('llamada_pasajero', 'Llamada al pasajero'),
        ('llamada_policia', 'Llamada a la policía'),
        ('cerrado', 'Cerrado'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='incidente')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='abierto')
    followup_notes = models.TextField(blank=True, null=True, help_text="Notas de seguimiento y acciones tomadas")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.id} - {self.user.username} - {self.report_type}"

# Modelos para las promociones y referidos
class Promotion(models.Model):
    TARGET_CHOICES = [
        ('conductor', 'Solo conductores'),
        ('usuario', 'Solo usuarios/pasajeros'),
        ('todos', 'Todos'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    bonus_amount = models.DecimalField(max_digits=8, decimal_places=2)
    min_invited_users = models.PositiveIntegerField(default=0, help_text="Cantidad mínima de usuarios invitados")
    min_trips = models.PositiveIntegerField(default=0, help_text="Cantidad mínima de viajes realizados")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_group = models.CharField(max_length=20, choices=TARGET_CHOICES, default='todos')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Promociones generales"


class UserPromotion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_promotions')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='user_promotions')
    awarded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.promotion.name}"   
    
    class Meta:
        verbose_name_plural = "Promociones personalizadas"   

# politicas y condiciones de bonos y referidos
class Policy(models.Model):
    title = models.CharField(max_length=100, default="Políticas y Condiciones")
    content = models.TextField(help_text="Texto completo de las políticas y condiciones para bonos y referidos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title         