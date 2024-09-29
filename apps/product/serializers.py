from itertools import product
from typing import List, Dict
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
    children = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListSerializer(child=serializers.CharField()))
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'children']


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

    def create(self, validated_data):
        validated_data['comment_id'] = self.context['cid']
        return super().create(validated_data)


class MiniCommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True)

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'images', 'created_date']


class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True)
    user = UserProfileSerializer(read_only=True)
    tree = serializers.SerializerMethodField(read_only=True)

    def get_tree(self, obj) -> List[Dict]:
        if obj.parent is None:
            return MiniCommentSerializer(obj.tree.exclude(id=obj.id), many=True).data
        return []

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'images', 'top_level_comment_id', 'tree', 'created_date']
        read_only_fields = ['tree']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        validated_data['user_id'] = self.context['request'].user.id
        validated_data['product_id'] = self.context['pid']
        obj = super().create(validated_data)
        for image in images:
            CommentImage.objects.create(comment=obj, image=image['image'])
        return obj
