from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Vista base para / y /api/
def api_root_view(request):
    return JsonResponse({
        "message": "Bienvenido a la API de MoveNet",
        "endpoints": [
            "/api/token/",
            "/api/register/",
            "/api/register/driver/",
            "/api/register/passenger/",
            "/api/driver/status/",
            "/docs/",
            "/redoc/"
        ]
    })

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="MoveNet API",
        default_version='v1',
        description="Documentación de la API de MoveNet",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', api_root_view),  # Para que / muestre algo
    path('api/', api_root_view),  # Para que /api/ muestre algo

    path('admin/', admin.site.urls),
    path('api/token/', include('backend.urls_auth')),  # Ruta para token si la usas
    path('api/', include('users.urls')),  # Todas las rutas de users.views

    # Swagger UI
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
