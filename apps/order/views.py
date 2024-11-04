from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.models import (Order,
                               OrderItem,
                               # CartItem,
                               Promo)
from apps.order.serializers import (
    PromoSerializer,
    # CartItemSerializer,
    OrderSerializer,
    OrderPostSerializer
)
from apps.product.models import Wishlist
from apps.product.utils import CreateViewSetMixin
# from .utils import generate_receipt_pdf

class CheckPromo(generics.GenericAPIView):
    serializer_class = PromoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class CartItemViewSet(viewsets.ModelViewSet):
#     serializer_class = CartItemSerializer
#     queryset = CartItem.objects.all()
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)


class OrderViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    model = Order
    serializer_post_class = OrderPostSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CreateOrderFromWishlistAPIView(APIView):
    def post(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        if not wishlist_items:
            return Response({"error": "No items in wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            "user": request.user.id,
            "total_amount": 0,
            "items": []
        }

        for item in wishlist_items:
            product = item.product
            item_amount = product.price * (1 - (product.discount / 100))  # Chegirma bilan narx
            order_data["items"].append({
                "product": product.id,
                "quantity": 1,  # Yoki foydalanuvchi tomonidan tanlangan miqdor
                "unit_price": product.price,
                "discount": product.discount or 0,
            })
            order_data["total_amount"] += item_amount

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()

            # Wishlistni tozalash
            wishlist_items.delete()

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

