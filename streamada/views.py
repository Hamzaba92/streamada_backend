from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from streamada.serializers import UserSerializer, LoginSerializer
from django.shortcuts import redirect
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from .serializers import PasswordResetSerializer
from rest_framework.views import APIView
from django.utils.decorators import method_decorator

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User successfully registered'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            return redirect('http://localhost:4200/login')
        else:
            return redirect('http://localhost:4200/login')
    else:
        return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny]) 
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'message': 'Login erfolgreich.'
        }, status=200)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, Token.DoesNotExist):
        pass
    return Response({'message': 'Logout erfolgreich.'}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "E-mail send"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)