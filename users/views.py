from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

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


# ✅ LOGIN DE USUARIO con JWT
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Se requieren email y contraseña.'}, status=400)

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Correo no registrado.'}, status=404)

    user = authenticate(username=user.username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        role = 'desconocido'
        if hasattr(user, 'driver'):
            role = 'conductor'
        elif hasattr(user, 'passenger'):
            role = 'pasajero'

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role
            }
        }, status=200)
    else:
        return Response({'error': 'Contraseña incorrecta.'}, status=401)


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

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Este nombre de usuario ya está registrado. Inicia sesión.'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Este correo ya está registrado. Inicia sesión.'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)

        if role == 'conductor':
            Driver.objects.create(user=user)
        elif role == 'pasajero':
            Passenger.objects.create(user=user)

        return Response({
            'message': 'Usuario registrado correctamente.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role
            }
        }, status=status.HTTP_201_CREATED)

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
