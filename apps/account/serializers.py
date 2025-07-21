from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .validators import validate_phone_number
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from apps.account.models import User, UserToken
from .models import UserLocation, NewBlock, Advice, Call, Banner, Carta
from django.contrib.auth import get_user_model


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=11, required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ]
    )
    password1 = serializers.CharField(write_only=True, validators=[validate_password],
                                      help_text=password_validators_help_texts)
    password2 = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Telefon raqami allaqachon ishlatilgan.")
        return value

    def validate(self, attrs):
        phone = attrs.get('phone')
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('Email already registered')
        if password1 != password2:
            raise ValidationError('Passwords do not match')
        return attrs

    class Meta:
        model = User
        fields = ['name', 'phone', 'password1', 'password2']

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            phone=validated_data['phone'],
            password=validated_data['password1']
        )
        user.is_active = True
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['created_date'] = user.created_date.strftime('%d.%m.%Y %H:%M:%S')
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'phone', 'avatar', 'is_active', 'is_superuser', 'is_staff', 'modified_date',
            'created_date')


class SuperUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'name', 'password')

    def create(self, validated_data):
        validated_data['is_superuser'] = True
        validated_data['is_staff'] = True
        validated_data['is_active'] = True
        user = User.objects.create_superuser(**validated_data)
        return user


class UserLocationSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'location', 'latitude', 'longitude', 'floor', 'apartment', ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'avatar', ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar']

class UserDeleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = User
        fields = ['password',]

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Noto'g'ri parol")
        return value


class NewBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewBlock
        fields = ['id', 'title', 'description', 'image', 'created_date']


class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'title', 'description']


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['id', 'phone', 'telegram', 'instagram', 'tiktok', 'facebook']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'image']


class CartaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carta
        fields = ['id', 'user_carta_name', 'bank_name', 'carta_number', 'bank_number']
