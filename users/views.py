from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, permissions, serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import Driver, Passenger, Trip
from .serializers import TripSerializer, DriverLocationUpdateSerializer

from math import radians, cos, sin, asin, sqrt

# Importa el decorador de drf-yasg para documentar el body en Swagger
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

# ==========================
# Vistas de Usuarios y Roles
# ==========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "¡Accediste a una vista protegida con éxito!"})

@api_view(['POST'])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    referred_by_username = request.data.get('referred_by')  # Opcional

    if not username or not password:
        return Response({'error': 'Faltan campos obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        referred_by = None
        if referred_by_username:
            try:
                referred_by = User.objects.get(username=referred_by_username)
            except User.DoesNotExist:
                return Response({'error': 'El código de referido no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, referred_by=referred_by)
        return Response({'message': 'Usuario registrado exitosamente.'}, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response({'error': 'El nombre de usuario ya existe.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_driver(request):
    user = request.user
    data = request.data

    if hasattr(user, 'driver'):
        return Response({"detail": "Este usuario ya es conductor."}, status=400)

    driver = Driver.objects.create(
        user=user,
        license_number=data.get("license_number"),
        car_plate=data.get("car_plate"),
    )
    return Response({"detail": "Conductor registrado. Pendiente de aprobación."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_passenger(request):
    user = request.user

    if hasattr(user, 'passenger'):
        return Response({"detail": "Este usuario ya es pasajero."}, status=400)

    passenger = Passenger.objects.create(user=user)
    return Response({"detail": "Pasajero registrado correctamente."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_driver_status(request):
    user = request.user
    try:
        driver = user.driver
        return Response({
            "is_approved": driver.is_approved,
            "license_number": driver.license_number,
            "car_plate": driver.car_plate
        })
    except Driver.DoesNotExist:
        return Response({"detail": "No es un conductor registrado."}, status=404)

# ==========================
# Vistas para Viajes (Trip)
# ==========================

class TripListView(generics.ListAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

class TripCreateView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        passenger = getattr(self.request.user, 'passenger', None)
        if not passenger:
            raise serializers.ValidationError("El usuario no es un pasajero registrado.")
        serializer.save(passenger=passenger)

# ==========================
# Asignar conductor más cercano a un viaje pendiente (mock notificación)
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_driver_to_trip(request, trip_id):
    """
    Asigna automáticamente el conductor aprobado y disponible más cercano a un viaje pendiente.
    Simula una notificación al conductor (mock).
    """
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Viaje no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if trip.status != 'pending':
        return Response({'error': 'El viaje no está pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

    # Obtener todos los conductores aprobados y disponibles
    available_drivers = Driver.objects.filter(is_approved=True).exclude(trips__status__in=['assigned', 'in_progress'])

    if not available_drivers.exists():
        return Response({'error': 'No hay conductores disponibles.'}, status=status.HTTP_404_NOT_FOUND)

    # Función para calcular la distancia entre dos puntos (Haversine)
    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radio de la Tierra en km
        return c * r

    # Buscar el conductor más cercano usando current_lat/current_lng de Driver
    min_distance = None
    nearest_driver = None
    for driver in available_drivers:
        current_lat = driver.current_lat
        current_lng = driver.current_lng
        if current_lat is None or current_lng is None:
            continue

        distance = haversine(
            trip.origin_lat, trip.origin_lng,
            current_lat, current_lng
        )
        if (min_distance is None) or (distance < min_distance):
            min_distance = distance
            nearest_driver = driver

    if not nearest_driver:
        return Response({'error': 'No hay conductores con ubicación disponible.'}, status=status.HTTP_404_NOT_FOUND)

    trip.driver = nearest_driver
    trip.status = 'assigned'
    trip.save()

    # Mock de notificación al conductor
    notification_message = f"¡Conductor {nearest_driver.user.username} asignado al viaje {trip.id}! (Mock de notificación)"

    return Response({
        'message': 'Conductor más cercano asignado exitosamente.',
        'notification': notification_message,
        'distance_km': round(min_distance, 2),
        'trip': TripSerializer(trip).data
    }, status=status.HTTP_200_OK)

# ==========================
# Endpoint para actualizar ubicación del conductor
# ==========================

@swagger_auto_schema(method='post', request_body=DriverLocationUpdateSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location(request):
    """
    Permite que un conductor actualice su ubicación actual (latitud y longitud).
    """
    user = request.user
    if not hasattr(user, 'driver'):
        return Response({'error': 'Solo los conductores pueden actualizar ubicación.'}, status=403)
    serializer = DriverLocationUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    lat = serializer.validated_data['lat']
    lng = serializer.validated_data['lng']
    user.driver.current_lat = lat
    user.driver.current_lng = lng
    user.driver.save()
    return Response({'message': 'Ubicación actualizada correctamente.'})