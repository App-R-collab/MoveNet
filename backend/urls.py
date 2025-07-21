from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/token/', include('backend.urls_auth')),

    # User routes
    path('api/', include('users.urls')),

    # Redirect root URL to a valid endpoint (e.g., /api/register/)
    re_path(r'^$', RedirectView.as_view(url='/api/register/', permanent=False)),

    # Redirect /api/ to /api/register/ if you want something to show
    re_path(r'^api/$', RedirectView.as_view(url='/api/register/', permanent=False)),
]
