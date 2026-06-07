from django.contrib import admin
from .models import (
    Bearing, BearingStock, BearingType, PrecisionClass, 
    SealType, Material, Manufacturer, Order, OrderItem,
    TechnicalDoc, Customer, OrderStatus
)

@admin.register(BearingType)
class BearingTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(PrecisionClass)
class PrecisionClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'description']

@admin.register(SealType)
class SealTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

class BearingStockInline(admin.StackedInline):
    model = BearingStock
    can_delete = False
    extra = 0

@admin.register(Bearing)
class BearingAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'name', 'manufacturer', 'price_display', 'stock_display']
    list_filter = ['type', 'manufacturer', 'material']
    search_fields = ['article', 'name']
    inlines = [BearingStockInline]
    
    def price_display(self, obj):
        if hasattr(obj, 'stock') and obj.stock:
            return f"{obj.stock.price} руб."
        return "Нет цены"
    price_display.short_description = 'Цена'
    
    def stock_display(self, obj):
        if hasattr(obj, 'stock') and obj.stock:
            return obj.stock.stock_quantity
        return 0
    stock_display.short_description = 'Остаток'

@admin.register(TechnicalDoc)
class TechnicalDocAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'bearing', 'uploaded_at']
    list_filter = ['bearing']
    search_fields = ['file_name', 'bearing__article', 'bearing__name']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email']
    search_fields = ['name', 'phone', 'email']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price_at_order']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'customer', 'status', 'total_amount', 'created_at', 'manager']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    inlines = [OrderItemInline]