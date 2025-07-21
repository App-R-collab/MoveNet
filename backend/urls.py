from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticación con JWT (usa backend/urls_auth.py)
    path('api/token/', include('backend.urls_auth')),

    # Rutas de usuarios: registro, conductor, pasajero, estado, etc.
    path('api/', include('users.urls')),
]

