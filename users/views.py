from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, permissions, serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import Driver, Passenger, Trip
from .serializers import TripSerializer

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
# Asignar conductor a un viaje pendiente (mock)
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_driver_to_trip(request, trip_id):
    """
    Asigna automáticamente un conductor disponible (aprobado) a un viaje pendiente.
    """
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Viaje no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if trip.status != 'pending':
        return Response({'error': 'El viaje no está pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

    # Buscar un conductor aprobado que no esté asignado a un viaje en curso
    available_driver = Driver.objects.filter(is_approved=True).exclude(trips__status__in=['assigned', 'in_progress']).first()

    if not available_driver:
        return Response({'error': 'No hay conductores disponibles.'}, status=status.HTTP_404_NOT_FOUND)

    trip.driver = available_driver
    trip.status = 'assigned'
    trip.save()

    return Response({
        'message': 'Conductor asignado exitosamente.',
        'trip': TripSerializer(trip).data
    }, status=status.HTTP_200_OK)