from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework.permissions import IsAuthenticated
from .tasks import ecommerce_send_email
from apps.account.models import User, UserToken
from apps.account.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .models import UserLocation
from .serializers import UserLocationSerializer


class UserLocationUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tgan foydalanuvchilarga ruxsat

    def get_object(self):
        # Faqat hozirgi foydalanuvchining lokatsiyasi ustida ishlash uchun
        return self.request.user.location


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = UserToken.objects.create(user=user)
        ecommerce_send_email.apply_async(("Activation Token Code", str(token.token), [user.phone]), )
        data = {
            'success': True,
            'detail': 'Activation Token Code has been sent to your phone.',
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        data = {
            'success': True,
            'detail': 'Your account has been deactivated.',
        }
        return Response(data, status=status.HTTP_200_OK)
