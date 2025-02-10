from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import User, UserLocation
from apps.account.serializers import UserLocationSerializer
from apps.order.models import (
    Order,
    CartItem,
    Promo,
)
from apps.product.serializers import ProductSerializer
from drf_spectacular.utils import extend_schema_field


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

        @extend_schema_field(serializers.FloatField())
        def get_amount(self, obj) -> float:
            return float(obj.product.price) * obj.quantity


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
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class UserSerializersOrder(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializersOrder(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    promo = serializers.CharField(required=False, allow_blank=True)
    # location = UserLocationSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'location_data', 'file', 'items', 'promo', 'get_amount', 'is_delivered', 'modified_date',
                  'created_date',
                  ]


class OrderPostSerializer(serializers.ModelSerializer):
    # items = serializers.PrimaryKeyRelatedField(queryset=CartItem.objects.all(), many=True)
    items = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    location = serializers.PrimaryKeyRelatedField(queryset=UserLocation.objects.all(), required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'promo', 'location', 'file', 'get_amount', 'modified_date', 'created_date']
        read_only_fields = ['user', 'items', 'amount']

    def validate(self, attrs):
        # Promo kod tekshiruvi
        user = self.context.get('request').user
        location_id = self.context['request'].data.get('location')

        if location_id:
            try:
                location = UserLocation.objects.get(id=location_id, user=user)
            except UserLocation.DoesNotExist:
                raise ValidationError("Berilgan locatsiya mavjud emas yoki sizga tegishli emas.")
        else:
            # Agar locatsiya berilmagan bo'lsa, foydalanuvchining oxirgi locatsiyasini olishga urinadi
            location = UserLocation.objects.filter(user=user).last()
            if not location:
                raise ValidationError("Locatsiya topilmadi. Iltimos, locatsiyani qo'shing.")

        attrs['location'] = location
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
        validated_data['user'] = self.context['request'].user  # User ni to‘g‘ridan-to‘g‘ri o‘rnatish
        return super().create(validated_data)
