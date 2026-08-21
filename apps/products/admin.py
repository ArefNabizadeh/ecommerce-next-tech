# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Brand, Category, Product, ProductImage,
    ProductSpecification, Review, Wishlist,FlashSale
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_featured', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['is_active', 'is_featured']

    def products_count(self, obj):
        return obj.products_count

    products_count.short_description = "تعداد محصولات"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_featured', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['is_active', 'is_featured']

    def products_count(self, obj):
        return obj.products_count

    products_count.short_description = "تعداد محصولات"


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['key', 'value']
    classes = ['collapse']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order']
    classes = ['collapse']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'price', 'final_price', 'stock',
        'category', 'brand', 'is_active', 'is_featured'
    ]
    list_filter = ['category', 'brand', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSpecificationInline, ProductImageInline]
    readonly_fields = ['views', 'created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'description', 'category', 'brand')
        }),
        ('قیمت و موجودی', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('مشخصات', {
            'fields': ('color', 'warranty')
        }),
        ('تصویر', {
            'fields': ('image',)
        }),
        ('وضعیت و آمار', {
            'fields': ('is_active', 'is_featured', 'views', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'order']
    list_filter = ['product']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'key', 'value']
    list_filter = ['key']
    search_fields = ['product__name', 'key', 'value']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """ادمین نظرات محصولات"""

    list_display = [
        'product',
        'user',
        'rating',
        'is_approved',
        # 'has_order',
        'created_at',
    ]

    list_filter = [
        'is_approved',
        'rating',
        'created_at',
    ]

    search_fields = [
        'product__name',
        'user__username',
        'comment',
    ]

    list_editable = [
        'is_approved',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'product',
                'user',
                'order',
                'rating',
                'comment',
            )
        }),
        ('وضعیت', {
            'fields': (
                'is_approved',
                'created_at',
                'updated_at',
            )
        }),
    )

    @admin.display(description="وضعیت خرید")
    def has_order(self, obj):
        """نمایش اینکه کاربر محصول را خریده یا نه"""

        try:
            if obj.order:
                return format_html(
                    '<span style="color: green;">✔ خریداری شده</span>'
                )

            return format_html(
                '<span style="color: orange;">❌ خریداری نشده</span>'
            )

        except Exception:
            return format_html(
                '<span style="color: orange;">❌ خریداری نشده</span>'
            )

    actions = [
        'approve_reviews',
        'unapprove_reviews',
    ]

    @admin.action(description="تایید نظرات انتخاب شده")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)

        self.message_user(
            request,
            f"{updated} نظر تایید شدند."
        )

    @admin.action(description="غیرفعال کردن نظرات انتخاب شده")
    def unapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)

        self.message_user(
            request,
            f"{updated} نظر غیرفعال شدند."
        )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['created_at']


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    """ادمین فروش ویژه"""
    list_display = ['title', 'is_active', 'hours', 'minutes', 'seconds', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'is_active')
        }),
        ('تنظیمات تایمر', {
            'fields': ('hours', 'minutes', 'seconds')
        }),
    )