from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .validators import validate_phone_number
from rest_framework.validators import UniqueValidator

from apps.account.models import User, UserToken
from .models import UserLocation


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ['latitude', 'longitude']

    def update(self, instance, validated_data):
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    location = UserLocationSerializer()
    phone = serializers.CharField(
        max_length=12, required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()), validate_phone_number
        ]
    )

    class Meta:
        model = User
        fields = ['name', 'phone', 'location',]

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        user = User.objects.create_user(
            name=validated_data['name'],
            phone=validated_data['phone'],
        )
        user.is_active = True
        user.set_unusable_password()
        user.save()
        UserLocation.objects.create(user=user, **location_data)
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

