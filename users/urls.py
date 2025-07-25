from django.urls import path
from .views import (
    protected_view,
    register_view,
    register_driver,
    register_passenger,
    check_driver_status,
    TripListCreateView,
    assign_driver_to_trip,
    UpdateDriverLocationView,
    TripStatusUpdateView,
    ChatMessageListCreateView
)

urlpatterns = [
    path('protected/', protected_view, name='protected'),
    path('register/', register_view, name='register_user'),
    path('register/driver/', register_driver, name='register_driver'),
    path('register/passenger/', register_passenger, name='register_passenger'),
    path('driver/status/', check_driver_status, name='check_driver_status'),

    # Endpoints para viajes
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/<int:trip_id>/assign_driver/', assign_driver_to_trip, name='assign-driver-to-trip'),
    path('driver/update-location/', UpdateDriverLocationView.as_view(), name='update_driver_location'),
    path('trips/<int:pk>/status/', TripStatusUpdateView.as_view(), name='trip-status-update'),  
    path('chats/<int:trip_id>/', ChatMessageListCreateView.as_view(), name='chat-messages'),
]
