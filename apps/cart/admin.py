from django.contrib import admin
from .models import Cart,CartItem
# Register your models here.

class CartItemInline(admin.StackedInline):
    model = CartItem
    extra = 0
    fields = ['product','quantity','total_price']
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_price', 'total_items', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']

    def total_price(self, obj):
        return obj.items.count()

    total_price.short_description = "قیمت کل"

    def total_items(self, obj):
        return obj.total_items

    total_items.short_description = "تعداد آیتم‌ها"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price']
    list_filter = ['cart__user']
    search_fields = ['product__name', 'cart__user__username']