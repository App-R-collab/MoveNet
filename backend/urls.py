from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse

# Vista informativa por defecto
def api_root(request):
    return JsonResponse({
        "message": "Bienvenido a la API de MoveNet",
        "endpoints": [
            "/api/token/",
            "/api/register/",
            "/api/register/driver/",
            "/api/register/passenger/",
            "/api/driver/status/",
        ]
    })

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación con JWT
    path('api/token/', include('backend.urls_auth')),

    # Rutas de la app users
    path('api/', include('users.urls')),

    # Ruta base para mostrar algo si entran a / o /api/
    path('', api_root),
    path('api/', api_root),
]