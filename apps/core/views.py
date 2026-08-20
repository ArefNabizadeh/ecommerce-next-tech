from django.utils import timezone

from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from apps.products.models import Product, Category, Wishlist, FlashSale, Review
from apps.discounts.models import Coupon


# Create your views here.


def home(request):
    # slider_products = Product.objects.filter(
    #     is_active=True
    # ).select_related(
    #     'category',
    #     'brand'
    # )[:5]
    slider_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]

    if slider_products.count() < 5:
        extra_products = Product.objects.filter(
            is_active=True,
            is_featured=True
        ).exclude(
            id__in=slider_products.values_list('id', flat=True)
        )[:5 - slider_products.count()]
        slider_products = list(slider_products) + list(extra_products)

    popular_categories = Category.objects.filter(
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(
        product_count__gt=0
    ).order_by('-product_count')[:8]

    now = timezone.now()
    featured_coupon = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now
    ).filter(
        Q(valid_to__gte=now) | Q(valid_to__isnull=True)
    ).order_by('-discount_value').first()

    flash_sale_products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False
    ).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('?')[:4]

    if flash_sale_products.count() < 4:
        extra_products = Product.objects.filter(
            is_active=True,
            is_featured=True
        ).exclude(
            id__in=flash_sale_products.values_list('id', flat=True)
        )[:4 - flash_sale_products.count()]
        flash_sale_products = list(flash_sale_products) + list(extra_products)

    # ==========================================
    # ===== تایمر فروش ویژه (قابل تنظیم) =====
    # ==========================================

    # روش ۱: از دیتابیس (اگه مدل FlashSale دارید)
    flash_sale = FlashSale.objects.filter(is_active=True).first()
    if flash_sale:
        flash_sale_hours = flash_sale.hours
        flash_sale_minutes = flash_sale.minutes
        flash_sale_seconds = flash_sale.seconds
    else:
        flash_sale_hours = 12
        flash_sale_minutes = 0
        flash_sale_seconds = 0

    # روش ۲: از تنظیمات (settings.py)
    # from django.conf import settings
    # flash_sale_hours = getattr(settings, 'FLASH_SALE_HOURS', 12)
    # flash_sale_minutes = getattr(settings, 'FLASH_SALE_MINUTES', 0)
    # flash_sale_seconds = getattr(settings, 'FLASH_SALE_SECONDS', 0)

    # روش ۳: ساده (مقدار ثابت)
    # flash_sale_hours = 5
    # flash_sale_minutes = 0
    # flash_sale_seconds = 0

    # ===== لیست ID محصولات موجود در علاقه‌مندی‌های کاربر =====
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-created_at')[:4]

    new_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:4]

    reviews = Review.objects.filter(
        is_approved=True
    ).select_related(
        'user',
        'user__profile',  # برای آواتار
        'product',
        'order'
    ).order_by('-created_at')[:3]

    try:
        from apps.blog.models import Article
        latest_articles = Article.objects.filter(
            status='published'
        ).select_related('category').order_by('-created_at')[:3]
    except:
        latest_articles = []

    context = {"brands": [
        {'name': 'Apple', 'slug': 'apple', 'icon': 'apple.svg'},
        {'name': 'Samsung', 'slug': 'samsung', 'icon': 'samsung.svg'},
        {'name': 'Sony', 'slug': 'sony', 'icon': 'sony.svg'},
        {'name': 'Asus', 'slug': 'asus', 'icon': 'asus.svg'},
        {'name': 'MSI', 'slug': 'msi', 'icon': 'msi.svg'},
        {'name': 'HP', 'slug': 'hp', 'icon': 'hp.svg'},
        {'name': 'Dell', 'slug': 'dell', 'icon': 'dell.svg'},
        {'name': 'Lenovo', 'slug': 'lenovo', 'icon': 'lenovo.svg'},
        {'name': 'Acer', 'slug': 'acer', 'icon': 'acer.svg'},
        {'name': 'Intel', 'slug': 'intel', 'icon': 'intel.svg'},
        {'name': 'AMD', 'slug': 'amd', 'icon': 'amd.svg'},
        {'name': 'NVIDIA', 'slug': 'nvidia', 'icon': 'nvidia.svg'},

        {'name': 'JBL', 'slug': 'jbl', 'icon': 'jbl.svg'},
        {'name': 'Xiaomi', 'slug': 'xiaomi', 'icon': 'xiaomi.svg'},
    ], 'slider_products': slider_products, 'popular_categories': popular_categories,
        'featured_coupon': featured_coupon, 'flash_sale_products': flash_sale_products,
        'wishlist_product_ids': wishlist_product_ids,
        'flash_sale_hours': flash_sale_hours,
        'flash_sale_minutes': flash_sale_minutes,
        'flash_sale_seconds': flash_sale_seconds, 'featured_products': featured_products,'new_products': new_products,'reviews': reviews,'latest_articles': latest_articles,}
    return render(request, "home.html", context)


def error_404_view(request, exception):
    """صفحه ۴۰۴ - صفحه پیدا نشد (با exception برای handler404)"""
    return render(request, 'errors/404.html', status=404)


def error_500_view(request):
    """صفحه ۵۰۰ - خطای سرور"""
    return render(request, 'errors/500.html', status=500)


# ===== پیش‌نمایش برای تست (بدون exception) =====
def error_404_preview(request):
    """پیش‌نمایش صفحه ۴۰۴ در حالت DEBUG (بدون exception)"""
    return render(request, 'errors/404.html')


def error_500_preview(request):
    """پیش‌نمایش صفحه ۵۰۰ در حالت DEBUG"""
    return render(request, 'errors/500.html')

def clear_messages(request):
    """پاک کردن همه پیام‌های سشن"""
    storage = messages.get_messages(request)
    storage.used = True  # این باعث می‌شود پیام‌ها مصرف شده در نظر گرفته شوند
    return HttpResponse('OK')
