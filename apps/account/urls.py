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
    # SendEmailView,
    # VerifyEmailView,
    LoginView,
    # ChangePasswordView,
    # ResetPasswordView,
    UserProfileRUDView,
)

router = DefaultRouter()

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    # path('mail/send/', SendEmailView.as_view(), name='send-mail'),
    # path('mail/verify/', VerifyEmailView.as_view(), name='send-verify'),
    path('login/', LoginView.as_view(), name='login'),
    # path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    # path('password/reset/', ResetPasswordView.as_view(), name='password-reset'),
    # path('profile/<int:pk>/', UserProfileRUDView.as_view(), name='password-reset'),
]




