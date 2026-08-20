# apps/orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'total_price',
        'status', 'payment_status', 'shipping_method', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'shipping_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'order_number', 'total_price', 'subtotal', 'discount')
        }),
        ('اطلاعات ارسال', {
            'fields': ('address', 'phone', 'shipping_method', 'shipping_cost')
        }),
        ('وضعیت', {
            'fields': ('status', 'payment_status', 'payment_method', 'tracking_code')
        }),
        ('مالیات و سایر', {
            'fields': ('tax', 'note', 'created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    search_fields = ['product__name', 'order__order_number']
    list_filter = ['order__status']