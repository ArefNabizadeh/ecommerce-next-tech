from django.contrib.auth import get_user_model
from apps.cart.models import Cart
from apps.products.models import Wishlist, Category, Brand,Product
from django.db.models import Count
User = get_user_model()


def user_context(request):
    return {'user': request.user,
            'is_authenticated': request.user.is_authenticated, }


def navbar_data(request):
    """ارسال داده‌های نوار ناوبری به تمام تمپلیت‌ها"""
    context = {
        'cart_items_count': 0,
        'wishlist_count': 0,
        'categories': Category.objects.filter(is_active=True)[:4],
        'brands': Brand.objects.filter(is_active=True)[:3],
    }

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        context['cart_items_count'] = cart.items.count()
        context['wishlist_count'] = Wishlist.objects.filter(user=request.user).count()

    return context


def popular_searches(request):
    """دریافت جستجوهای محبوب از دیتابیس"""
    # می‌توانی از جدول جستجوهای ذخیره‌شده استفاده کنی
    # یا بر اساس محصولات پرفروش و پرطرفدار
    popular = [
        'گوشی موبایل',
        'لپ‌تاپ',
        'هدفون',
        'ساعت هوشمند',
        'سامسونگ',
        'اپل'
    ]
    return {'popular_searches': popular}
