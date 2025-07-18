from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# Vista protegida que ya tenías (la dejamos igual)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "¡Accediste a una vista protegida con éxito!"})

# Nueva vista de registro con lógica de referido opcional
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
