from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.order.views import (
    CheckPromo,
    PromoCreateView,
    CartItemViewSet,
    # OrderViewSet,
)

router = DefaultRouter()
router.register('cart-items', CartItemViewSet, basename='cart-items')
# router.register('', OrderViewSet, basename='order')


urlpatterns = [
    path('check_promo/', CheckPromo.as_view()),
    path('promo/create/', PromoCreateView.as_view(), name='promo-create'),
    path('', include(router.urls)),
]