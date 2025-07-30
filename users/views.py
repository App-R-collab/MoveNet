from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Trip, ChatMessage, Driver, Passenger
from .serializers import (
    TripSerializer,
    DriverLocationUpdateSerializer,
    TripStatusUpdateSerializer,
    ChatMessageSerializer,
    RegisterSerializer,
)

# ✅ VISTA PROTEGIDA PARA TEST DE AUTENTICACIÓN
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def protected_view(request):
    return Response({'message': f'Hola, {request.user.username}. Estás autenticado correctamente.'})


# ✅ REGISTRO DE USUARIO BASE CON EMAIL Y ROL
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        role = serializer.validated_data['role']

        user = User.objects.create_user(username=username, password=password, email=email)

        # Asignar rol
        if role == 'conductor':
            Driver.objects.create(user=user)
        elif role == 'pasajero':
            Passenger.objects.create(user=user)

        return Response({'message': 'Usuario registrado correctamente.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ REGISTRO DE CONDUCTOR
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_driver(request):
    user = request.user
    if hasattr(user, 'driver'):
        return Response({'error': 'Este usuario ya es un conductor.'}, status=400)
    Driver.objects.create(user=user)
    return Response({'message': 'Conductor registrado correctamente.'})


# ✅ REGISTRO DE PASAJERO
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_passenger(request):
    user = request.user
    if hasattr(user, 'passenger'):
        return Response({'error': 'Este usuario ya es un pasajero.'}, status=400)
    Passenger.objects.create(user=user)
    return Response({'message': 'Pasajero registrado correctamente.'})


# ✅ ESTADO DE CONDUCTOR
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_driver_status(request):
    user = request.user
    is_driver = hasattr(user, 'driver')
    return Response({'is_driver': is_driver})


# ✅ ASIGNAR CONDUCTOR A UN VIAJE
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_driver_to_trip(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        driver = request.user.driver
        if trip.driver is not None:
            return Response({'error': 'Este viaje ya tiene un conductor asignado.'}, status=400)
        trip.driver = driver
        trip.save()
        return Response({'message': 'Conductor asignado al viaje.'})
    except Trip.DoesNotExist:
        return Response({'error': 'Viaje no encontrado.'}, status=404)
    except AttributeError:
        return Response({'error': 'Este usuario no es un conductor.'}, status=400)


# ✅ LISTA Y CREA VIAJES
class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all().order_by('-created_at')
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user.passenger)


# ✅ ACTUALIZAR ESTADO DEL VIAJE
class TripStatusUpdateView(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


# ✅ ACTUALIZAR UBICACIÓN DEL CONDUCTOR
class UpdateDriverLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DriverLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            driver = request.user.driver
            driver.current_lat = serializer.validated_data['lat']
            driver.current_lng = serializer.validated_data['lng']
            driver.save()
            return Response({'message': 'Ubicación actualizada correctamente'})
        return Response(serializer.errors, status=400)


# ✅ ENVIAR MENSAJE EN CHAT DEL VIAJE
class SendChatMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        message_text = request.data.get('message')

        if not message_text:
            return Response({'error': 'Mensaje vacío'}, status=400)

        message = ChatMessage.objects.create(
            trip=trip,
            sender=request.user,
            message=message_text
        )
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=201)


# ✅ LISTAR MENSAJES DE UN VIAJE
class TripChatMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return ChatMessage.objects.filter(trip__id=trip_id).order_by('timestamp')


# ✅ LISTA Y CREA MENSAJES EN UNA SOLA VISTA
class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return ChatMessage.objects.filter(trip_id=trip_id).order_by('timestamp')

    def perform_create(self, serializer):
        trip_id = self.kwargs['trip_id']
        trip = Trip.objects.get(id=trip_id)
        serializer.save(sender=self.request.user, trip=trip)
