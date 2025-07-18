from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Driver, Passenger

# Registro del modelo de usuario personalizado con el panel de Django
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "referral_code", "referred_by")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("referral_code", "referred_by")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Driver)
admin.site.register(Passenger)
