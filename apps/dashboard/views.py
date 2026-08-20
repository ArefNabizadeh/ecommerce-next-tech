from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.accounts.models import Profile, Address
from apps.products.models import Product, Wishlist
from apps.orders.models import Order, OrderItem
from apps.accounts.forms import ProfileForm, AddressForm

@login_required
def dashboard_view(request):

    user = request.user

    total_orders = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, status='Pending').count()
    completed_orders = Order.objects.filter(user=user, status='delivered').count()

    wishlist_count = Wishlist.objects.filter(user=user).count()
    addresses_count = Address.objects.filter(user=user).count()

    reward_points = 0
    wallet_balance = 0

    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'wishlist_count': wishlist_count,
        'addresses_count': addresses_count,
        'reward_points': reward_points,
        'wallet_balance': wallet_balance,
        'recent_orders': recent_orders,}

    return render(request,'dashboard/dashboard.html',context)

@login_required
def profile_view(request):
    user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    # آمار
    total_orders = Order.objects.filter(user=user).count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    addresses_count = Address.objects.filter(user=user).count()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات شما با موفقیت بروزرسانی شد ✅')
            return redirect('apps.dashboard:profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'total_orders': total_orders,
        'wishlist_count': wishlist_count,
        'addresses_count': addresses_count,
    }

    return render(request, 'dashboard/profile.html', context)


# ================================================
# ===== سفارشات =====
# ================================================

@login_required
def orders_view(request):
    """لیست سفارشات کاربر"""

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # ===== آمار وضعیت‌ها =====
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    preparing_orders = orders.filter(status='processing').count()
    shipping_orders = orders.filter(status='shipped').count()
    delivered_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()

    # ===== صفحه‌بندی =====
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'shipping_orders': shipping_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    }

    return render(request, 'dashboard/orders.html', context)


@login_required
def order_detail_view(request, order_id):
    """جزئیات یک سفارش"""

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'orders/order_detail.html', context)


# ================================================
# ===== آدرس‌ها =====
# ================================================

@login_required
def addresses_view(request):
    """صفحه آدرس‌های کاربر"""

    addresses = Address.objects.filter(user=request.user)

    context = {
        'addresses': addresses,
    }

    return render(request, 'dashboard/addresses.html', context)


@login_required
def add_address_view(request):
    """افزودن آدرس جدید"""

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'آدرس با موفقیت اضافه شد ✅')
            return redirect('apps.dashboard:addresses')
    else:
        form = AddressForm()

    # اگر فرم خطا داشته باشد، به صفحه آدرس‌ها برمی‌گردیم
    return redirect('apps.dashboard:addresses')


@login_required
def edit_address_view(request, address_id):
    """ویرایش آدرس"""

    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'آدرس با موفقیت ویرایش شد ✏️')
            return redirect('apps.dashboard:addresses')

    return redirect('apps.dashboard:addresses')


@login_required
def delete_address_view(request, address_id):
    """حذف آدرس"""

    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'آدرس با موفقیت حذف شد 🗑️')

    return redirect('apps.dashboard:addresses')


@login_required
def set_default_address_view(request, address_id):
    """تنظیم آدرس به عنوان پیش‌فرض"""

    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        # همه آدرس‌های کاربر را غیرپیش‌فرض کن
        Address.objects.filter(user=request.user, is_default=True).update(
            is_default=False)
        # آدرس مورد نظر را پیش‌فرض کن
        address.is_default = True
        address.save()
        messages.success(request, 'آدرس پیش‌فرض با موفقیت تنظیم شد ✅')

    return redirect('apps.dashboard:addresses')


# ================================================
# ===== علاقه‌مندی‌ها =====
# ================================================

@login_required
def wishlist_view(request):
    """صفحه علاقه‌مندی‌های کاربر"""

    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-created_at')
    wishlist_count = wishlist_items.count()

    context = {
        'wishlist': wishlist_items,
        'wishlist_count': wishlist_count,
    }

    return render(request, 'dashboard/wishlist.html', context)


@login_required
def remove_wishlist_view(request, wishlist_id):
    """حذف محصول از علاقه‌مندی‌ها"""

    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)

    if request.method == 'POST':
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        messages.success(request, f'{product_name} از علاقه‌مندی‌ها حذف شد ❤️')

    return redirect('apps.dashboard:wishlist')