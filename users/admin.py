from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Driver, Passenger, Trip, Report

# Panel personalizado para usuarios
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "referral_code", "referred_by")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("referral_code", "referred_by")}),
    )
    search_fields = ("username", "email", "referral_code")
    list_filter = ("is_active", "is_staff")

# Panel personalizado para conductores
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'car_plate', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'car_plate', 'license_number')
    fields = ('user', 'license_number', 'car_plate', 'is_approved', 'current_lat', 'current_lng')
    readonly_fields = ('current_lat', 'current_lng')

# Panel personalizado para pasajeros
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('user_username',)
    search_fields = ('user__username',)

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Usuario'

# Panel personalizado para viajes
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'origin_lat', 'origin_lng',
        'destination_lat', 'destination_lng',
        'passenger_username', 'driver_username',
        'status_display',
        'fare',
        'created_at',
    )
    list_filter = ('status', 'driver')
    search_fields = (
        'id',
        'passenger__user__username',
        'driver__user__username',
        'origin_lat', 'origin_lng',
        'destination_lat', 'destination_lng',
    )
    ordering = ('-created_at',)
    list_per_page = 25

    fields = (
        'passenger', 'driver',
        'origin_lat', 'origin_lng',
        'destination_lat', 'destination_lng',
        'status', 'fare', 'created_at', 'updated_at'
    )
    readonly_fields = ('fare', 'created_at', 'updated_at')

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Estado'

    def passenger_username(self, obj):
        return obj.passenger.user.username if obj.passenger else '-'
    passenger_username.short_description = 'Pasajero'

    def driver_username(self, obj):
        return obj.driver.user.username if obj.driver else '-'
    driver_username.short_description = 'Conductor'

# Registro de los paneles personalizados
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Passenger, PassengerAdmin)

# Títulos personalizados para el panel de administración
admin.site.site_header = "MoveNet - Administración"
admin.site.site_title = "MoveNet Admin"
admin.site.index_title = "Bienvenido al Panel MoveNet"

# Registrar y personalizar el panel de admin
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trip', 'report_type', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('user__username', 'trip__id', 'description')
    readonly_fields = ('created_at',)

admin.site.register(Report, ReportAdmin)