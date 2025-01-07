"""
Register:
    - /register/ -> send code to user via mail
    - /mail/verify/ -> verify code -> activate, give token

Login:
    - /login/ -> give token

Verify Account:
    - /mail/send/ -> send code to user via mail
    - /mail/verify/ -> verify code -> activate, give token

Change Password:
    - /password/change/ -> change password

Reset Password:
        - /mail/send/ -> send code to user via mail
        - /mail/verify/ -> verify code -> activate, give token
    - /password/reset/ -> reset password
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegisterView,
    LoginView,
    UserLocationUpdateAPIView,
    SuperUserCreateView,
    UserProfileAPIView
)

router = DefaultRouter()
router.register('location', UserLocationUpdateAPIView)
urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('superuser/create/', SuperUserCreateView.as_view(), name='superuser-create'),

]
