from django.contrib import admin
from django.db.models import Sum
from .models import (
    CustomUser, Driver, Passenger, Trip, Report,
    Promotion, UserPromotion, Policy, Earning,
    ResumenGananciasProxy, ChatMessage  # 👈 Añadido ChatMessage aquí
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'referral_code', 'referred_by')
    search_fields = ('username', 'email', 'referral_code')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'car_plate', 'is_approved')

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'driver', 'status', 'fare', 'created_at')
    list_filter = ('status',)
    search_fields = ('passenger__user__username', 'driver__user__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report_type', 'status', 'created_at')
    list_filter = ('status', 'report_type')
    search_fields = ('user__username',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'bonus_amount', 'start_date', 'end_date', 'target_group')
    list_filter = ('target_group',)
    search_fields = ('name',)

@admin.register(UserPromotion)
class UserPromotionAdmin(admin.ModelAdmin):
    list_display = ('user', 'promotion', 'awarded_at')
    search_fields = ('user__username', 'promotion__name')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'earning_type', 'created_at')
    list_filter = ('earning_type',)
    search_fields = ('user__username', 'description')

# ✅ ADMIN DE RESUMEN DE GANANCIAS
@admin.register(ResumenGananciasProxy)
class ResumenGananciasAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'total_promociones',
        'total_general'
    )
    search_fields = ('username',)

    def get_queryset(self, request):
        return CustomUser.objects.all()

    def total_promociones(self, obj):
        total = Earning.objects.filter(
            user=obj,
            earning_type='promocion'
        ).aggregate(total=Sum('amount'))['total']
        return total or 0
    total_promociones.short_description = 'Total Promociones'

    def total_general(self, obj):
        total = Earning.objects.filter(
            user=obj
        ).aggregate(total=Sum('amount'))['total']
        return total or 0
    total_general.short_description = 'Total Ganado'

# ✅ CHAT MENSAJES
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'sender', 'message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message', 'sender__username', 'trip__id')
