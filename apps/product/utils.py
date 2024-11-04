from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from apps.order.models import Order


def generate_receipt_pdf(order_id):
    # Buyurtma ma'lumotlarini olish
    order = Order.objects.get(id=order_id)

    # PDF faylini yaratish
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # PDF ga ma'lumotlarni yozish
    p.drawString(100, 750, f"Chek №: {order.id}")
    p.drawString(100, 730, f"Foydalanuvchi: {order.user.username}")
    p.drawString(100, 710, f"Umumiy miqdor: {order.amount} so'm")
    p.drawString(100, 690, f"Yaratilgan sana: {order.created_date.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 670, "Mahsulotlar:")

    y = 650
    for item in order.items.all():
        p.drawString(100, y, f"{item.product.name} - {item.quantity} dona - {item.amount} so'm")
        y -= 20  # Qator oralig'i

    # PDF ni tugatish
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


class CreateViewSetMixin:
    def get_model(self):
        if self.model is None:
            raise ImproperlyConfigured("You must specify a model")
        return self.model

    def get_serializer_class(self):
        if self.serializer_post_class is None:
            raise ImproperlyConfigured("You must specify a serializer class")

        if self.action in ['list', 'retrieve']:
            return super().get_serializer_class()
        return self.serializer_post_class

    def create(self, request, *args, **kwargs):
        obj_id = super().create(request, *args, **kwargs).data.get('id')
        obj = get_object_or_404(self.get_model(), id=obj_id)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
