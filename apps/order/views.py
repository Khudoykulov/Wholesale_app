from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from apps.order.models import (
    Order,
    CartItem,
    Promo
)
from apps.order.serializers import (PromoSerializer,
                                    PromoPostSerializer,
                                    CartItemSerializer, CartItemPostSerializer,
                                    OrderSerializer,
                                    OrderPostSerializer
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='clear-cart')
    def clear_cart(self, request):
        user_cart_items = self.get_queryset()
        deleted_count = user_cart_items.count()
        user_cart_items.delete()
        return Response(
            {'message': f'{deleted_count} ta mahsulot savatchadan o\'chirildi.'},
            status=status.HTTP_200_OK
        )


class OrderViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    model = Order
    serializer_post_class = OrderPostSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Agar foydalanuvchi superuser bo'lsa, barcha orderlarni qaytaramiz
        if self.request.user.is_superuser:
            return self.queryset
        # Aks holda faqat o'zining orderlarini qaytaramiz
        return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        # Request obyektini serializer kontekstiga uzatish
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Buyurtma muvaffaqiyatli o'chirildi."},
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        instance.delete()


class OrderPDFView(APIView):
    def get(self, request, order_id):
        try:
            # Orderni topish
            order = Order.objects.get(id=order_id)

            # Agar order yetkazilgan bo'lsa, PDFni generate qilamiz
            if order.is_delivered:
                pdf_response = order.generate_pdf_receipt  # Bu yerda modelning metodini chaqiramiz
                return pdf_response  # PDFni qaytaramiz

            # Agar order hali yetkazilmagan bo'lsa, 404 yoki mos javob qaytarish
            return Response({"detail": "Order not delivered yet."}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class MarkOrderAsDelivered(APIView):
    permission_classes = [IsAuthenticated]  # Foydalanuvchi autentifikatsiyalangan bo'lishi kerak

    def patch(self, request, pk=None):
        try:
            # Orderni topish (faqat o'z foydalanuvchisining ordersini topish)
            order = Order.objects.get(pk=pk, user=request.user)
            order.is_delivered = True
            order.save()
            # Endi PDFni generate qilamiz
            pdf_response = order.generate_pdf_receipt  # Bu yerda modelning metodini chaqiramiz

            # PDFni qaytarish
            return pdf_response
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
