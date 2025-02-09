from email.policy import default
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from apps.account.models import User, UserLocation
from apps.product.models import Product

from django.utils import timezone
from django.http import HttpResponse
from apps.order.utils import generate_receipt_pdf  # PDF yaratish funksiyasi


class Promo(models.Model):
    name = models.CharField(max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promos')
    description = models.TextField(null=True, blank=True)
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    min_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(100.00)])
    members = models.ManyToManyField(User, blank=True)
    expire_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='cart_items')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name if self.product else "order_items"

    @property
    def get_amount(self):
        return (float(self.product.price) * ((100 - (self.product.discount or 0)) / 100)) * self.quantity


from django.core.exceptions import ValidationError
import mimetypes


def validate_file_type(value):
    allowed_mime_types = [
        "image/",  # Barcha rasm formatlari (JPEG, PNG, GIF, WEBP, SVG, TIFF, BMP va boshqalar)
        "application/pdf",  # PDF fayllar
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/zip",  # ZIP fayllar
        "application/x-rar-compressed",  # RAR fayllar
        "application/x-7z-compressed",  # 7z fayllar
    ]

    mime_type, _ = mimetypes.guess_type(value.name)

    if not mime_type:
        raise ValidationError("Noto‘g‘ri fayl turi!")

    # Barcha rasm formatlarini avtomatik qabul qilish uchun "image/" bilan boshlanganlarini tekshiramiz
    if not any(mime_type.startswith(allowed) for allowed in allowed_mime_types):
        raise ValidationError("Faqat rasm yoki hujjat fayllarini yuklash mumkin!")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    location = models.ForeignKey(UserLocation, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='orders_location')
    items = models.ManyToManyField(CartItem)
    file = models.FileField(blank=True, null=True,
                            upload_to="uploads/",
                            validators=[validate_file_type]
                            )
    promo = models.CharField(max_length=8, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def get_amount(self):
        if self.promo:
            try:
                promo_object = Promo.objects.get(name=self.promo)
                return float(
                    sum(item.get_amount for item in self.items.all()) * (((100 - promo_object.discount) or 0) / 100))
            except Promo.DoesNotExist:
                # Agar mos promo mavjud bo'lmasa, chegirmasiz qaytaramiz
                return sum(item.get_amount for item in self.items.all())
        return sum(item.get_amount for item in self.items.all())

    @property
    def generate_pdf_receipt(self):
        if self.is_delivered:
            # Order ma'lumotlari va mahsulotlar ro'yxatini yig'ish
            order_data = {
                'user': self.user.name,
                'order_date': self.created_date.strftime("%Y-%m-%d %H:%M"),
                'amount': str(self.get_amount),
                'items': [
                    {
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'price': str(item.get_amount)
                    }
                    for item in self.items.all()
                ]
            }
            # PDF generatsiya qilish
            pdf_content = generate_receipt_pdf(order_data)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="order_{self.id}_receipt.pdf"'
            return response
        else:
            return None
