from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import CartItem, Order, Promo
from django.urls import path, reverse
from django.http import HttpResponse
from django.db import transaction
from django.utils.safestring import mark_safe
import json

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'discount', 'min_price', 'expire_date', 'is_expired', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_expired',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_date',)
    search_fields = ('user__username', 'user__full_name')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'get_amount', 'created_date')
    search_fields = ('product__name', 'user__username', 'user__full_name')
    date_hierarchy = 'created_date'
    readonly_fields = ('created_date',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'get_user_name', 'get_user_phone', 'get_file_link', 'get_amount', 'location_address', 'created_date')
    list_display_links = ('id', 'get_user_name', 'get_amount',)
    fields = ['get_user_name', 'get_user_phone', 'formatted_location_data', 'created_date']
    date_hierarchy = 'created_date'
    readonly_fields = ('get_user_name', 'get_user_phone', 'modified_date', 'created_date', 'formatted_location_data')


    def formatted_location_data(self, obj):
        if obj.location_data:
            formatted_json = json.dumps(obj.location_data, indent=4, ensure_ascii=False)
            return mark_safe(f"""
            <style>
                pre {{
                    background-color: #282C34;
                    color: #61DAFB;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 18px;
                    overflow-x: auto;
                }}
            </style>
            <pre>{formatted_json}</pre>
            """)
        return "N/A"
    formatted_location_data.short_description = "Formatted Location Data"

    def location_address(self, obj):
        if obj.location_data:
            return obj.location_data.get('location', 'N/A')  # Agar `address` bo‘lsa, chiqaramiz
        return "N/A"

    location_address.short_description = "Location Address"

    def get_file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" download>{}</a>', obj.file.url, "Download File 📂")
        return "No File"

    get_file_link.short_description = "File"

    def get_user_name(self, obj):
        return obj.user.name

    get_user_name.short_description = "User Name"

    def get_user_phone(self, obj):
        return obj.user.phone

    get_user_phone.short_description = "User Phone"

    def save_model(self, request, obj, form, change):
        """Buyurtma saqlanayotganda mahsulot miqdorini tekshirish va kamaytirish"""
        with transaction.atomic():  # Tranzaksiya blokiga olish
            super().save_model(request, obj, form, change)  # Avval Order saqlanadi

            obj.refresh_from_db()  # Yangi obyekt uchun ID ni yuklash
            items = obj.items.all()  # Endi ManyToMany maydoni ishlaydi

            for item in items:
                product = item.product
                if item.quantity > product.quantity:
                    raise ValidationError(
                        f"{product.name} mahsulotidan yetarli miqdorda mavjud emas. "
                        f"Qoldiq: {product.quantity} ta."
                    )

                product.quantity -= item.quantity  # Mahsulot miqdorini kamaytirish
                product.save()

        super().save_model(request, obj, form, change)

    def pdf_receipt_link(self, obj):
        if obj.is_delivered:
            url = reverse('admin:order-pdf', args=[obj.id])
            return format_html('<a href="{}">Download PDF</a>', url)
        return "Not available"

    pdf_receipt_link.short_description = 'PDF Receipt'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/pdf/', self.admin_site.admin_view(self.download_pdf), name='order-pdf'),
        ]
        return custom_urls + urls

    def download_pdf(self, request, order_id):
        order = self.get_object(request, order_id)
        if order and order.is_delivered:
            response = HttpResponse(order.generate_pdf_receipt, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="order_{order_id}_receipt.pdf"'
            return response
        return HttpResponse("Receipt not available", status=404)
