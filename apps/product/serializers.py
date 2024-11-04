from itertools import product
from typing import List, Dict

from django.template.context_processors import request
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import (
    Category,
    Tag,
    Product,
    ProductImage,
    Trade,
    Like,
    Wishlist,
    Rank,
    Comment,
    CommentImage,
)
from ..account.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.CharField(required=False, allow_blank=True)
    children = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListSerializer(child=serializers.CharField()))
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'parent', 'children']

    def create(self, validated_data):
        parent_id = validated_data.pop('parent', None)
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(id=int(parent_id))
            except (Category.DoesNotExist, ValueError):
                raise serializers.ValidationError({"parent": "Parent category not found or invalid ID"})
        category = Category.objects.create(parent=parent, **validated_data)
        return category



class MiniCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
        extra_kwargs = {'image': {'required': False}}


class ProductSerializer(serializers.ModelSerializer):
    # images = ProductImageSerializer(many=True, read_only=True)
    category = MiniCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'discount', 'views', 'sold_count', 'image_urls',
                  'tags',
                  'average_rank', 'get_quantity', 'get_likes_count', 'is_available', 'modified_date', 'created_date']
        read_only_fields = ['views', 'is_available']


class MiniProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = MiniCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'views', 'sold_count', 'images', 'average_rank',
                  'get_quantity', 'get_likes_count', 'is_available', 'modified_date', 'created_date']
        read_only_fields = ['views', 'is_available']


class ProductPostSerializer(serializers.ModelSerializer):
    # images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'discount', 'image_urls', 'tags']

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.save()
        return obj


class TradeSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    action_name = serializers.CharField(read_only=True, source='get_action_display')

    class Meta:
        model = Trade
        fields = ['id', 'product', 'user', 'action_name', 'quantity', 'description', 'created_date']
        read_only_fields = ['user']


class TradePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'product', 'user', 'action', 'quantity', 'description', 'created_date']
        read_only_fields = ['user']

    def validate(self, data):
        product = data.get('product')
        user = self.context['request'].user
        action = data.get('action')
        quantity = data.get('quantity', 0)

        # 1. Foydalanuvchi va mahsulot foydalanuvchisini solishtirish
        # if product and user and product.user != user:
        #     print('qwwwwwwwwwwwwwwwwwwwwwwww')
        #     raise serializers.ValidationError("You can only create trades for your own products.")
        # print(product.user)
        print(data)
        print(user)
        # 2. Agar action Outcome bo'lsa, mahsulotning mavjud miqdorini tekshirish
        if action == 2:  # Outcome
            total_income_quantity = sum(
                trade.quantity for trade in product.trades.filter(action=1)
            )
            total_outcome_quantity = sum(
                trade.quantity for trade in product.trades.filter(action=2)
            )
            available_quantity = total_income_quantity - total_outcome_quantity

            if quantity > available_quantity:
                raise serializers.ValidationError(
                    f"Insufficient product quantity for this outcome action. Available quantity: {available_quantity}"
                )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class WishListSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'user']


class WishListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'product', 'user']


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'product']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class RankSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)

    class Meta:
        model = Rank
        fields = ['id', 'product', 'rank']

    def create(self, validated_data):
        user = self.context['request'].user
        pid = self.context['pid']
        validated_data['user_id'] = user.id
        validated_data['product_id'] = pid
        return super().create(validated_data)


class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ['id', 'image']
        extra_kwargs = {'image': {'required': False}}

    def create(self, validated_data):
        return super().create(validated_data)


class MiniCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'comment_image_url', 'created_date']


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    tree = serializers.SerializerMethodField(read_only=True)

    def get_tree(self, obj) -> List[Dict]:
        if obj.parent is None:
            return MiniCommentSerializer(obj.tree.exclude(id=obj.id), many=True).data
        return []

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'comment_image_url', 'top_level_comment_id', 'tree',
                  'created_date']
        read_only_fields = ['tree']

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        validated_data['product_id'] = self.context['pid']
        obj = super().create(validated_data)
        return obj
