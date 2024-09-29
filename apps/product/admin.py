from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline, TranslationStackedInline

from apps.product.models import (
    Category,
    Tag,
    Product,
    ProductImage,
    Trade,
    Wishlist,
    Like,
    Rank,
    Comment,
    CommentImage,
)


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('id', 'parent', 'name', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    # inlines = (ProductImageInline,)
    list_display = (
        'id', 'name', 'category', 'price', 'discount', 'average_rank', 'get_quantity', 'get_likes_count',
        'is_available',
        'created_date')
    readonly_fields = (
        'average_rank', 'get_quantity', 'get_likes_count', 'is_available', 'modified_date', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    autocomplete_fields = ('category',)


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('product__name',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user')
    search_fields = ('product__name', 'user__name')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user')
    search_fields = ('product__name', 'user__name')


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rank')
    search_fields = ('product__name', 'user__name')
    list_filter = ('rank',)


@admin.register(CommentImage)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'parent', 'top_level_comment_id', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('product__name', 'user__name', 'parent__name')
    readonly_fields = ('top_level_comment_id', 'created_date')
