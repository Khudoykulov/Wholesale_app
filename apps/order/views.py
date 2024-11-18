from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.order.models import (
    # Order,
    CartItem,
    Promo
)
from apps.order.serializers import (PromoSerializer,
                                    PromoPostSerializer,
                                    CartItemSerializer, CartItemPostSerializer,
    # OrderSerializer,
    # OrderPostSerializer
                                    )
from apps.product.utils import CreateViewSetMixin


class PromoCreateView(generics.CreateAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Yaratilayotgan promo foydalanuvchi bilan bog'lanadi
        serializer.save(user=self.request.user)


class CheckPromo(generics.ListCreateAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        # Serializerni user bilan chaqirish
        serializer = self.serializer_class(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = CartItem
    serializer_class = CartItemSerializer
    serializer_post_class = CartItemPostSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        CartItem.objects.all()
        return self.queryset.filter(user=self.request.user)

# class OrderViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
#     serializer_class = OrderSerializer
#     model = Order
#     serializer_post_class = OrderPostSerializer
#     queryset = Order.objects.all()
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)
