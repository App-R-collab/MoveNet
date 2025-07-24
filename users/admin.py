from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Driver, Passenger, Trip

# Registro del modelo de usuario personalizado con el panel de Django
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "referral_code", "referred_by")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("referral_code", "referred_by")}),
    )

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

    # Campos editables en el formulario de edición
    fields = (
        'passenger', 'driver',
        'origin_lat', 'origin_lng',
        'destination_lat', 'destination_lng',
        'status', 'fare', 'created_at', 'updated_at'
    )
    # Campos de solo lectura (no editables)
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

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Driver)
admin.site.register(Passenger)
# El registro de Trip ya está personalizado arriba con @admin.register(Trip)