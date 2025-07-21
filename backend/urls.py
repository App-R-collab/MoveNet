from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Vista base para / y /api/
def api_root_view(request):
    return JsonResponse({
        "message": "Bienvenido a la API de MoveNet",
        "endpoints": [
            "/api/token/",
            "/api/register/",
            "/api/register/driver/",
            "/api/register/passenger/",
            "/api/driver/status/"
        ]
    })

urlpatterns = [
    path('', api_root_view),  # Para que / muestre algo
    path('api/', api_root_view),  # Para que /api/ muestre algo

    path('admin/', admin.site.urls),
    path('api/token/', include('backend.urls_auth')),
    path('api/', include('users.urls')),
]
