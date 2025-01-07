from django.db import models
from django.db.models.signals import pre_save
from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, phone, name, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not password:
            raise ValueError('Superusers must have a password')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone=phone, name=name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=123, )
    phone = models.CharField(max_length=12, unique=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location')
    image = models.ImageField(null=True, blank=True, upload_to='Location_image/')
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    floor = models.CharField(max_length=123, null=True, blank=True)
    apartment = models.CharField(max_length=123, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location of {self.user}: ({self.latitude}, {self.longitude}), ({self.floor}, {self.apartment})"


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.PositiveIntegerField()
    is_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)


def user_token_pre_save(sender, instance, *args, **kwargs):
    if not instance.token:
        instance.token = randint(10000, 99999)


pre_save.connect(user_token_pre_save, sender=UserToken)



class NewBlock(models.Model):
    title = models.CharField(max_length=123)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='new_block_image/')
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title