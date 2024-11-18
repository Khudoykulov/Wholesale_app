from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import User
from apps.order.models import (
    Order,
    CartItem,
    Promo,
)
from apps.product.serializers import ProductSerializer


class PromoSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate(self, attrs):
        user = self.context.get('user')
        name = attrs.get('name')
        if name is None:
            raise ValidationError({'detail': "Name is required"})
        promo = Promo.objects.filter(name=name)
        if not promo.exists():
            raise ValidationError({'detail': "Promo does not exist"})
        if promo.last().is_expired:
            raise ValidationError({'detail': "Promo is expired"})
        if user in promo.last().members.all():
            return ValidationError({'detail': "Promo is already used"})
        return attrs


class PromoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ['id', 'name', 'user', 'description', 'discount', 'min_price', 'expire_date', 'is_expired',
                  'created_date']
        read_only_fields = ['id', 'created_date', 'is_expired']

    def validate(self, attrs):
        # Foydalanuvchi promo yaratganida chegirma va minimal narxni tekshirish
        discount = attrs.get('discount', 0)
        min_price = attrs.get('min_price', 0)

        if discount <= 0 or discount > 100:
            raise serializers.ValidationError({'discount': "Chegirma 1 dan 100 gacha bo'lishi kerak."})
        if min_price < 100.00:
            raise serializers.ValidationError({'min_price': "Minimal narx kamida 100 bo'lishi kerak."})

        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'user', 'quantity', 'get_amount', 'created_date']
        read_only_fields = ['user', 'created_date']
        extra_kwargs = {
            'product': {'required': True},
            'quantity': {'required': True},
        }


class CartItemPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'user', 'quantity', 'get_amount', 'created_date']
        read_only_fields = ['user', 'created_date']
        extra_kwargs = {
            'product': {'required': True},
            'quantity': {'required': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['is']
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class UserSerializersOrder(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializersOrder(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    promo = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'promo', 'get_amount', 'is_delivered', 'modified_date', 'created_date',
                  ]


class OrderPostSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(queryset=CartItem.objects.all(), many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'promo', 'get_amount', 'modified_date', 'created_date']
        read_only_fields = ['user', 'items', 'amount']

    def validate(self, attrs):
        # Promo kod tekshiruvi
        user = self.context.get('request').user
        promo_code = attrs.get('promo', None)
        if promo_code:
            try:
                promo = Promo.objects.get(name=promo_code)
                # Promo kodining muddati o'tganmi
                if promo.is_expired:
                    raise ValidationError("Promo kodining muddati o'tgan.")
                # Buyurtma miqdori minimal narxdan kichikmi?
                total_amount = sum(item.get_amount for item in attrs['items'])
                if total_amount < promo.min_price:
                    raise ValidationError(
                        f"Promo kodni ishlatish uchun buyurtma miqdori {promo.min_price} dan kam bo'lmasligi kerak.")
                # Foydalanuvchi promo koddan oldin foydalanganmi?
                if promo.members.filter(id=user.id).exists():
                    raise ValidationError("Siz bu promo kodni allaqachon ishlatgansiz.")
                # Promo kodni qo'shish
                promo.members.add(user)
                promo.save()
            except Promo.DoesNotExist:
                raise ValidationError("Promo kod mavjud emas.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')  # `request`ni context orqali olish
        user = request.user  # Hozirgi foydalanuvchi
        validated_data['user'] = user  # `user`ni validated_data'ga qo'shamiz
        items = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        # `Order`ga `items`ni qo'shamiz
        for item in items:
            order.items.add(item)

        return order
