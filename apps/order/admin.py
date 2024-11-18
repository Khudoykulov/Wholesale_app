from django.contrib import admin
from django.utils.html import format_html

from .models import CartItem, Order, Promo
from django.urls import path, reverse
from django.http import HttpResponse

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'discount', 'min_price', 'expire_date', 'is_expired', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_expired', )
    filter_horizontal = ('members', )
    readonly_fields = ('created_date', )
    search_fields = ('user__username', 'user__full_name')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'get_amount', 'created_date')
    search_fields = ('product__name', 'user__username', 'user__full_name')
    date_hierarchy = 'created_date'
    readonly_fields = ('created_date', )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_amount', 'is_delivered', 'pdf_receipt_link', 'created_date')
    list_display_links = ('id', 'user', 'get_amount',)
    date_hierarchy = 'created_date'
    readonly_fields = ('modified_date', 'created_date')
    search_fields = ('user__username', 'user__full_name')

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
