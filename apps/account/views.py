from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SuperUserCreateSerializer, UserSerializer,UserUpdateSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
# from .tasks import ecommerce_send_email
from apps.account.models import User, UserToken
from apps.account.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    NewBlockSerializer
)
from .permissions import IsOwnerOrReadOnly,IsAdminOrReadOnly
from .models import UserLocation, NewBlock
from .serializers import UserLocationSerializer
from ..product.permissions import IsAdminOrReadOnly


class UserLocationUpdateAPIView(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tgan foydalanuvchilarga ruxsat

    def get_queryset(self):
        # Faqat hozirgi foydalanuvchining lokatsiyasi ustida ishlash uchun
        return UserLocation.objects.filter(user=self.request.user)


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = UserToken.objects.create(user=user)
        # ecommerce_send_email.apply_async(("Activation Token Code", str(token.token), [user.phone]), )
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
    parser_classes = [MultiPartParser, FormParser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        data = {
            'success': True,
            'detail': 'Your account has been deactivated.',
        }
        return Response(data, status=status.HTTP_200_OK)


class SuperUserCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SuperUserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "Superuser  create success full"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserUpdateSerializer,
        responses=UserSerializer
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NewBlockListCreateView(generics.ListCreateAPIView):
    queryset = NewBlock.objects.all()
    serializer_class = NewBlockSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

class NewBlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewBlock.objects.all()
    serializer_class = NewBlockSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]