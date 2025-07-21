from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación con JWT
    path('api/token/', include('backend.urls_auth')),

    # Rutas de usuarios
    path('api/', include('users.urls')),

    # Redirección de / hacia /api/
    re_path(r'^$', RedirectView.as_view(url='/api/', permanent=False)),
]
