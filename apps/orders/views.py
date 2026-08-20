# apps/orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from apps.cart.models import Cart
from apps.products.models import Product, Review
from apps.accounts.models import Address, UserActivity  # ← اضافه شد
from .models import Order, OrderItem
from .forms import CheckoutForm
from apps.discounts.models import Coupon


@login_required
def order_list_view(request):
    """صفحه لیست سفارشات کاربر"""

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # ===== فیلتر وضعیت =====
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # ===== جستجو =====
    search_query = request.GET.get('q')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    # آمار وضعیت‌ها
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status='processing').count()
    shipped_orders = orders.filter(status='shipped').count()
    delivered_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()

    # صفحه‌بندی
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query,
    }

    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail_view(request, order_id):
    """صفحه جزئیات سفارش با امکان ثبت نظر"""

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all().select_related('product')

    # ===== دریافت نظرات ثبت شده برای محصولات این سفارش =====
    reviewed_products = Review.objects.filter(
        user=request.user,
        order=order
    ).values_list('product_id', flat=True)

    # ===== پردازش POST برای ثبت نظر =====
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not product_id or not rating or not comment:
            messages.error(request, 'لطفاً همه فیلدها را پر کنید.')
            return redirect('apps.orders:order_detail', order_id=order.id)

        product = get_object_or_404(Product, id=product_id, is_active=True)

        # ===== بررسی اینکه کاربر این محصول رو در این سفارش خریده =====
        if not order.items.filter(product_id=product_id).exists():
            messages.error(request, 'شما این محصول را در این سفارش خریداری نکرده‌اید.')
            return redirect('apps.orders:order_detail', order_id=order.id)

        # ===== بررسی اینکه کاربر قبلاً برای این محصول نظر نداده =====
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, 'شما قبلاً برای این محصول نظر داده‌اید.')
            return redirect('apps.orders:order_detail', order_id=order.id)

        # ===== ثبت نظر =====
        try:
            review = Review.objects.create(
                product=product,
                user=request.user,
                order=order,
                rating=int(rating),
                comment=comment,
                is_approved=False
            )

            # ===== ثبت فعالیت =====
            UserActivity.log_activity(
                user=request.user,
                activity_type='review_added',
                message=f'نظر برای محصول {product.name} ثبت شد',
                icon='star',
                metadata={
                    'product_id': product.id,
                    'product_name': product.name,
                    'rating': rating
                },
                request=request
            )

            messages.success(
                request,
                '✅ نظر شما با موفقیت ثبت شد. پس از تایید ادمین نمایش داده می‌شود.'
            )
        except Exception as e:
            messages.error(request, f'خطا در ثبت نظر: {str(e)}')

        return redirect('apps.orders:order_detail', order_id=order.id)

    # محصولات پیشنهادی
    recommended_products = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=order_items.values_list('product_id', flat=True)
    ).order_by('-created_at')[:5]

    context = {
        'order': order,
        'order_items': order_items,
        'recommended_products': recommended_products,
        'reviewed_products': reviewed_products,
    }

    return render(request, 'orders/order_detail.html', context)


@login_required
def checkout_view(request):
    """صفحه تسویه حساب"""

    # دریافت سبد خرید کاربر
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product')

    if not cart_items.exists():
        messages.warning(request, 'سبد خرید شما خالی است.')
        return redirect('apps.cart:cart_detail')

    # ===== محاسبه قیمت‌ها (با تبدیل به int) =====
    subtotal = int(sum(item.total_price for item in cart_items))
    product_discount = int(sum(item.discount_amount for item in cart_items))

    # ===== اعمال کوپن از سشن =====
    coupon_discount = 0
    coupon_code = None
    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            is_valid, message = coupon.is_valid(request.user, subtotal)
            if is_valid:
                coupon_discount = coupon.calculate_discount(subtotal)
                coupon_code = coupon.code
            else:
                # حذف کوپن از سشن اگر معتبر نیست
                if 'coupon_id' in request.session:
                    del request.session['coupon_id']
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
                if 'coupon_discount' in request.session:
                    del request.session['coupon_discount']
                messages.warning(request, message)
        except Coupon.DoesNotExist:
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            if 'coupon_discount' in request.session:
                del request.session['coupon_discount']

    # ===== تخفیف نهایی =====
    total_discount = product_discount + coupon_discount

    # ===== هزینه ارسال =====
    # دریافت از POST یا GET
    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'standard')
    else:
        shipping_method = request.GET.get('shipping', 'standard')

    shipping_cost_map = {
        'standard': 0,
        'express': 25000,
        'premium': 50000,
    }
    shipping_cost = shipping_cost_map.get(shipping_method, 0)

    # ===== مالیات (۹٪) روی مبلغ مشمول =====
    taxable_amount = subtotal - total_discount
    tax = int(taxable_amount * 0.09) if taxable_amount > 0 else 0

    # ===== قیمت نهایی =====
    total_price = taxable_amount + shipping_cost + tax

    # آدرس‌های کاربر
    addresses = Address.objects.filter(user=request.user)

    # ===== پردازش POST =====
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        address_id = request.POST.get('address_id')
        shipping_method = request.POST.get('shipping_method', 'standard')
        payment_method = request.POST.get('payment_method', 'online')
        note = request.POST.get('note', '')

        # ===== محاسبه مجدد هزینه ارسال (برای اطمینان) =====
        shipping_cost = shipping_cost_map.get(shipping_method, 0)

        # ===== اعتبارسنجی آدرس =====
        if not address_id:
            messages.error(request, 'لطفاً یک آدرس را انتخاب کنید.')
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'addresses': addresses,
                'subtotal': subtotal,
                'discount': total_discount,
                'shipping_cost': shipping_cost,
                'tax': tax,
                'total_price': total_price,
                'coupon_code': coupon_code,
                'coupon_discount': coupon_discount,
                'selected_shipping': shipping_method,
            })

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, 'آدرس انتخاب شده معتبر نیست.')
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'addresses': addresses,
                'subtotal': subtotal,
                'discount': total_discount,
                'shipping_cost': shipping_cost,
                'tax': tax,
                'total_price': total_price,
                'coupon_code': coupon_code,
                'coupon_discount': coupon_discount,
                'selected_shipping': shipping_method,
            })

        # ===== بررسی اعتبار فرم =====
        if not form.is_valid():
            messages.error(request, 'لطفاً اطلاعات را به‌درستی وارد کنید.')
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'addresses': addresses,
                'subtotal': subtotal,
                'discount': total_discount,
                'shipping_cost': shipping_cost,
                'tax': tax,
                'total_price': total_price,
                'coupon_code': coupon_code,
                'coupon_discount': coupon_discount,
                'selected_shipping': shipping_method,
            })

        # ===== ایجاد سفارش با تراکنش اتمی =====
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=address.street_address,
                    phone=address.phone,
                    subtotal=subtotal,
                    discount=total_discount,
                    shipping_cost=shipping_cost,
                    tax=tax,
                    total_price=total_price,
                    shipping_method=shipping_method,
                    payment_method=payment_method,
                    note=form.cleaned_data.get('note', '')
                )

                # ===== ایجاد آیتم‌های سفارش و کاهش موجودی =====
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.final_price
                    )

                    # کاهش موجودی محصول
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()

                # ===== استفاده از کوپن =====
                if coupon_id:
                    try:
                        coupon = Coupon.objects.get(id=coupon_id, is_active=True)
                        coupon.use_coupon(request.user)
                        # پاک کردن سشن کوپن
                        if 'coupon_id' in request.session:
                            del request.session['coupon_id']
                        if 'coupon_code' in request.session:
                            del request.session['coupon_code']
                        if 'coupon_discount' in request.session:
                            del request.session['coupon_discount']
                    except Coupon.DoesNotExist:
                        pass

                # ===== خالی کردن سبد خرید =====
                cart_items.delete()

                # ===== ثبت فعالیت =====
                UserActivity.log_activity(
                    user=request.user,
                    activity_type='order_created',
                    message=f'سفارش #{order.order_number} ثبت شد',
                    icon='shopping-bag',
                    metadata={
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'total_price': str(total_price)
                    },
                    request=request
                )

                messages.success(
                    request,
                    f'✅ سفارش شما با شماره #{order.order_number} با موفقیت ثبت شد.'
                )
                return redirect('apps.orders:order_detail', order_id=order.id)

        except Exception as e:
            messages.error(request, f'خطا در ثبت سفارش: {str(e)}')
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'addresses': addresses,
                'subtotal': subtotal,
                'discount': total_discount,
                'shipping_cost': shipping_cost,
                'tax': tax,
                'total_price': total_price,
                'coupon_code': coupon_code,
                'coupon_discount': coupon_discount,
                'selected_shipping': shipping_method,
            })

    # ===== GET =====
    form = CheckoutForm()
    context = {
        'form': form,
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'discount': total_discount,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total_price': total_price,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'selected_shipping': shipping_method,
    }

    return render(request, 'orders/checkout.html', context)


@login_required
def cancel_order_view(request, order_id):
    """لغو سفارش توسط کاربر"""

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        # فقط سفارشات در وضعیت 'pending' قابل لغو هستند
        if order.status != Order.OrderStatus.PENDING:
            messages.error(request, 'امکان لغو این سفارش وجود ندارد.')
            return redirect('apps.orders:order_detail', order_id=order.id)

        with transaction.atomic():
            # برگرداندن موجودی به انبار
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()

            # تغییر وضعیت سفارش
            order.status = Order.OrderStatus.CANCELLED
            order.save()

        # ===== ثبت فعالیت =====
        UserActivity.log_activity(
            user=request.user,
            activity_type='order_cancelled',
            message=f'سفارش #{order.order_number} لغو شد',
            icon='x-circle',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number
            },
            request=request
        )

        messages.success(request, f'سفارش #{order.order_number} با موفقیت لغو شد.')

    return redirect('apps.orders:order_detail', order_id=order.id)
