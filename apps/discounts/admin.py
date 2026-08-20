# apps/discounts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
    'discount_type',
    'discount_value',
    'is_active',]
    list_filter = ['is_active', 'discount_type', 'is_public', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    filter_horizontal = ['used_by']
    readonly_fields = ['used_count', 'created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('code', 'discount_type', 'discount_value', 'description')
        }),
        ('محدودیت‌ها', {
            'fields': ('min_order_amount', 'max_discount_amount', 'usage_limit',
                       'is_public', 'used_by')
        }),
        ('تاریخ اعتبار', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('آمار', {
            'fields': ('used_count', 'created_at', 'updated_at')
        }),
    )

    def discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        return f"{obj.discount_value:,} تومان"

    discount_display.short_description = "مقدار تخفیف"

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✔ فعال</span>')
        return format_html('<span style="color: red;">✘ غیرفعال</span>')

    is_active_display.short_description = "وضعیت"

    def validity_display(self, obj):
        now = timezone.now()
        if obj.valid_to:
            if now > obj.valid_to:
                return format_html('<span style="color: red;">منقضی شده</span>')
            days_left = (obj.valid_to - now).days
            return format_html(
                f'<span style="color: orange;">{days_left} روز باقی‌مانده</span>')
        return format_html('<span style="color: green;">نامحدود</span>')

    validity_display.short_description = "اعتبار"

    def status_badge(self, obj):
        """وضعیت فعلی کوپن - بدون استفاده از is_valid"""
        now = timezone.now()

        # بررسی دستی وضعیت
        if not obj.is_active:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px;">❌ غیرفعال</span>'
            )

        if obj.valid_to and now > obj.valid_to:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px;">❌ منقضی</span>'
            )

        if obj.usage_limit and obj.used_count >= obj.usage_limit:
            return format_html(
                '<span style="background-color: #f59e0b; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px;">⚠️ تکمیل شده</span>'
            )

        return format_html(
            '<span style="background-color: #22c55e; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px;">✅ فعال</span>'
        )

    status_badge.short_description = "وضعیت فعلی"

    actions = ['activate_coupons', 'deactivate_coupons']

    def activate_coupons(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} کد تخفیف فعال شدند.")

    activate_coupons.short_description = "فعال کردن کدهای انتخاب شده"

    def deactivate_coupons(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} کد تخفیف غیرفعال شدند.")

    deactivate_coupons.short_description = "غیرفعال کردن کدهای انتخاب شده"