from django.urls import path
from .views import (
    protected_view,
    register_view,
    register_driver,
    register_passenger,
    check_driver_status,
)

urlpatterns = [
    path('protected/', protected_view, name='protected'),
    path('register/', register_view, name='register_user'),
    path('register/driver/', register_driver, name='register_driver'),
    path('register/passenger/', register_passenger, name='register_passenger'),
    path('driver/status/', check_driver_status, name='check_driver_status'),
]
