from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .validators import validate_phone_number
from rest_framework.validators import UniqueValidator

from apps.account.models import User, UserToken


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=12, required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()), validate_phone_number
        ]
    )
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'phone',]

    # def create(self, validated_data):
    #     phone = validated_data.get('phone')
    #     user = super(UserRegisterSerializer, self).create(validated_data)
    #     user.save()
    #     return user
    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            phone=validated_data['phone'],
            # password=validated_data['password']
        )
        return user

    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     password1 = attrs.get('password1')
    #     password2 = attrs.get('password2')
    #     if User.objects.filter(email=email).exists():
    #         raise ValidationError('Email already registered')
    #     if password1 != password2:
    #         raise ValidationError('Passwords do not match')
    #     return attrs


# class SendEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#
#     class Meta:
#         fields = ['email']
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         if not User.objects.filter(email=email).exists():
#             raise ValidationError('Email does not exist')
#         return attrs


# class VerifyEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     token = serializers.IntegerField()
#
#     class Meta:
#         fields = ['email', 'token']
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         token = attrs.get('token')
#         if UserToken.objects.filter(user__email=email).exists():
#             user_token = UserToken.objects.filter(user__email=email).last()
#             if user_token.is_used:
#                 raise ValidationError('Verification code already used')
#             if token != user_token.token:
#                 raise ValidationError('Token does not match')
#             user_token.is_used = True
#             user = User.objects.get(email=email)
#             user.is_active = True
#             user_token.save()
#             user.save()
#             return attrs
#         raise ValidationError('Credentials are not valid')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['created_date'] = user.created_date.strftime('%d.%m.%Y %H:%M:%S')
        return token


# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(write_only=True, validators=[validate_password])
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, validators=[validate_password])
#
#     def validate(self, attrs):
#         old_password = attrs.get('old_password')
#         password = attrs.get('password')
#         password2 = attrs.get('password2')
#         if self.context['request'].user.check_password(old_password):
#             if old_password == password:
#                 raise ValidationError('Current must not equal to new password')
#             if password == password2:
#                 return attrs
#             raise ValidationError("Passwords do not match")
#         raise ValidationError('Old password does not match')
#
#     def create(self, validated_data):
#         password = validated_data.get('password')
#         user = self.context['request'].user
#         user.set_password(password)
#         user.save()
#         return user


# class ResetPasswordSerializer(serializers.Serializer):
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, validators=[validate_password])
#
#     def validate(self, attrs):
#         password = attrs.get('password')
#         password2 = attrs.get('password2')
#         if self.context['request'].user.check_password(password):
#             raise ValidationError('Current must not equal to new password')
#         if password == password2:
#             return attrs
#         raise ValidationError('Passwords do not match')
#
#     def create(self, validated_data):
#         password = validated_data.get('password')
#         user = self.context['request'].user
#         user.set_password(password)
#         user.save()
#         return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'phone', 'avatar', 'is_active', 'is_superuser', 'is_staff', 'modified_date',
            'created_date')
