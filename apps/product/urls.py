from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    TagViewSet,
    ProductViewSet,
    ProductImageViewSet,
    TradeViewSet,
    WishlistViewSet,
    LikeViewSet,
    RankViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('tags', TagViewSet)
router.register(r'(?P<pid>[0-9]+)/images', ProductImageViewSet)
router.register('trades', TradeViewSet)
router.register('wishlists', WishlistViewSet)
router.register('likes', LikeViewSet)
router.register('(?P<pid>[0-9]+)/ranks', RankViewSet)
router.register('(?P<pid>[0-9]+)/comments', CommentViewSet)
router.register('', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]