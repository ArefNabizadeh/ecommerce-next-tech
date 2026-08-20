# apps/dashboard/context_processors.py
from apps.products.models import Wishlist
from apps.orders.models import Order
from apps.accounts.models import Address


def dashboard_counts(request):
    """ارسال تعداد اقلام به همه صفحات"""
    context = {
        'wishlist_count': 0,
        'orders_count': 0,
        'addresses_count': 0,
    }

    if request.user.is_authenticated:
        context['wishlist_count'] = Wishlist.objects.filter(user=request.user).count()
        context['orders_count'] = Order.objects.filter(user=request.user).count()
        context['addresses_count'] = Address.objects.filter(user=request.user).count()

    return context