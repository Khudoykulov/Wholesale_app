# from rest_framework import viewsets, generics, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from apps.order.models import Order, OrderItem, CartItem, Promo
# from apps.order.serializers import PromoSerializer, CartItemSerializer, OrderSerializer, OrderPostSerializer
# from apps.product.utils import CreateViewSetMixin
#
#
# class CheckPromo(generics.GenericAPIView):
#     serializer_class = PromoSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class CartItemViewSet(viewsets.ModelViewSet):
#     serializer_class = CartItemSerializer
#     queryset = CartItem.objects.all()
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         CartItem.objects.all()
#         return self.queryset.filter(user=self.request.user)
#
#
# class OrderViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
#     serializer_class = OrderSerializer
#     model = Order
#     serializer_post_class = OrderPostSerializer
#     queryset = Order.objects.all()
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)