from rest_framework import serializers
from .models import (
    Bearing, BearingStock, TechnicalDoc, Customer, Order, OrderItem,
    StatusHistory, EmailNotification, BearingType, PrecisionClass,
    SealType, Material, Manufacturer, OrderStatus
)
from .utils import send_order_notification

class BearingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BearingType
        fields = ['id', 'name']

class PrecisionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecisionClass
        fields = ['id', 'code']

class SealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SealType
        fields = ['id', 'name']

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name']

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class TechnicalDocSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnicalDoc
        fields = ['id', 'file_name', 'file_url', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
class BearingListSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='stock.price', max_digits=12, decimal_places=2, read_only=True)
    stock_quantity = serializers.IntegerField(source='stock.stock_quantity', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Bearing
        fields = ['id', 'article', 'name', 'type_name', 'manufacturer_name', 
                  'image', 'price', 'stock_quantity']

class BearingDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source='stock.price', max_digits=12, decimal_places=2, read_only=True)
    stock_quantity = serializers.IntegerField(source='stock.stock_quantity', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    precision_class_code = serializers.CharField(source='precision_class.code', read_only=True)
    seal_type_name = serializers.CharField(source='seal_type.name', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    docs = TechnicalDocSerializer(many=True, read_only=True)

    class Meta:
        model = Bearing
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    bearing_name = serializers.CharField(source='bearing.name', read_only=True)
    bearing_article = serializers.CharField(source='bearing.article', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'bearing', 'bearing_name', 'bearing_article', 'quantity', 'price_at_order']

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_number', 'status', 'total_amount', 'created_at']

class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=255, write_only=True)
    customer_organization = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    customer_phone = serializers.CharField(max_length=20, write_only=True)
    customer_email = serializers.EmailField(write_only=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    order_number = serializers.CharField(read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_customer_phone(self, value):
        if not value.startswith('+79') or len(value) != 12:
            raise serializers.ValidationError("Телефон должен быть в формате +79xxxxxxxxx")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Корзина не может быть пустой")
        for item in value:
            if 'bearing_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Каждый элемент должен содержать bearing_id и quantity")
            try:
                bearing = Bearing.objects.get(id=item['bearing_id'])
                stock = bearing.stock
                if item['quantity'] > stock.stock_quantity:
                    raise serializers.ValidationError(f"Недостаточно товара: {bearing.name} (доступно {stock.stock_quantity})")
            except Bearing.DoesNotExist:
                raise serializers.ValidationError(f"Подшипник с id {item['bearing_id']} не найден")
        return value

    def create(self, validated_data):
        customer_name = validated_data['customer_name']
        customer_organization = validated_data.get('customer_organization', '')
        customer_phone = validated_data['customer_phone']
        customer_email = validated_data['customer_email']
        delivery_address = validated_data.get('delivery_address', '')
        items_data = validated_data['items']

        customer, created = Customer.objects.get_or_create(
            email=customer_email,
            defaults={
                'name': customer_name,
                'organization': customer_organization,
                'phone': customer_phone
            }
        )
        if not created:
            customer.name = customer_name
            customer.organization = customer_organization
            customer.phone = customer_phone
            customer.save()

        try:
            status = OrderStatus.objects.get(name='Принята')
        except OrderStatus.DoesNotExist:
            status = OrderStatus.objects.create(name='Принята')

        total_amount = 0
        for item in items_data:
            bearing = Bearing.objects.get(id=item['bearing_id'])
            total_amount += bearing.stock.price * item['quantity']


        order = Order.objects.create(
            customer=customer,
            delivery_address=delivery_address,
            status=status,
            total_amount=total_amount
        )

        for item in items_data:
            bearing = Bearing.objects.get(id=item['bearing_id'])
            OrderItem.objects.create(
                order=order,
                bearing=bearing,
                quantity=item['quantity'],
                price_at_order=bearing.stock.price
            )

            bearing.stock.stock_quantity -= item['quantity']
            bearing.stock.save()


        StatusHistory.objects.create(order=order, old_status=None, new_status=status)
        send_order_notification(order)


        self.instance = order
        return order

    def to_representation(self, instance):
        data = {
            'order_number': instance.order_number,
            'status': instance.status.name,
            'total_amount': instance.total_amount,
            'created_at': instance.created_at,
        }
        return data

class BearingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BearingType
        fields = ['id', 'name']

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name']

class SealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SealType
        fields = ['id', 'name']

class PrecisionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecisionClass
        fields = ['id', 'code']