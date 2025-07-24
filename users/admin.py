from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum
from .models import (
    CustomUser, Driver, Passenger, Trip, Report, Promotion, 
    UserPromotion, Policy, Earning, EarningSummary
)

# -------------------------- Usuarios --------------------------
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "referral_code", "referred_by")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("referral_code", "referred_by")}),
    )
    search_fields = ("username", "email", "referral_code")
    list_filter = ("is_active", "is_staff")

admin.site.register(CustomUser, CustomUserAdmin)

# -------------------------- Conductores --------------------------
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'car_plate', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'car_plate', 'license_number')
    fields = ('user', 'license_number', 'car_plate', 'is_approved', 'current_lat', 'current_lng')
    readonly_fields = ('current_lat', 'current_lng')

admin.site.register(Driver, DriverAdmin)

# -------------------------- Pasajeros --------------------------
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('user_username',)
    search_fields = ('user__username',)

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Usuario'

admin.site.register(Passenger, PassengerAdmin)

# -------------------------- Viajes --------------------------
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'origin_lat', 'origin_lng', 'destination_lat', 'destination_lng',
        'passenger_username', 'driver_username', 'status_display', 'fare', 'created_at',
    )
    list_filter = ('status', 'driver')
    search_fields = (
        'id', 'passenger__user__username', 'driver__user__username',
        'origin_lat', 'origin_lng', 'destination_lat', 'destination_lng',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    fields = (
        'passenger', 'driver', 'origin_lat', 'origin_lng', 'destination_lat', 
        'destination_lng', 'status', 'fare', 'created_at', 'updated_at'
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

# -------------------------- Reportes --------------------------
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trip', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('user__username', 'trip__id', 'description', 'followup_notes')
    fields = ('user', 'trip', 'report_type', 'description', 'status', 'followup_notes', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Report, ReportAdmin)

# -------------------------- Promociones --------------------------
admin.site.register(Promotion, admin.ModelAdmin)
admin.site.register(UserPromotion, admin.ModelAdmin)
admin.site.register(Policy, admin.ModelAdmin)

# -------------------------- Ganancias individuales --------------------------
class EarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'earning_type', 'related_trip', 'related_promotion', 'created_at')
    list_filter = ('earning_type', 'created_at')
    search_fields = ('user__username', 'description')
    fields = ('user', 'amount', 'earning_type', 'related_trip', 'related_promotion', 'description', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Earning, EarningAdmin)

# -------------------------- Resumen de Ganancias --------------------------
@admin.register(EarningSummary)
class EarningSummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_ganado')

    def get_queryset(self, request):
        users = CustomUser.objects.filter(earnings__isnull=False).distinct()
        return [EarningSummary(user=u) for u in users]

    def total_ganado(self, obj):
        return obj.total_ganado
    total_ganado.short_description = 'Total Ganado'
    total_ganado.admin_order_field = 'total_ganado'

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
