# apps/cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from .models import Cart, CartItem
from apps.discounts.models import Coupon


def get_or_create_cart(user):
    """دریافت یا ایجاد سبد خرید برای کاربر"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def cart_detail_view(request):
    """صفحه نمایش سبد خرید"""

    if not request.user.is_authenticated:
        messages.warning(request, 'برای مشاهده سبد خرید وارد شوید.')
        return redirect('apps.accounts:login')

    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all().select_related('product')

    # محاسبه قیمت‌ها (با تبدیل به int برای جلوگیری از خطا)
    cart_total = int(cart.total_price) if cart.total_price else 0
    discount = int(cart.total_discount) if cart.total_discount else 0

    # ===== اعمال کوپن =====
    coupon_id = request.session.get('coupon_id')
    coupon_discount = 0
    coupon_code = None

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            # بررسی مجدد اعتبار کوپن
            is_valid, message = coupon.is_valid(request.user, cart_total)
            if is_valid:
                coupon_discount = coupon.calculate_discount(cart_total)
                coupon_code = coupon.code
                # به‌روزرسانی مبلغ تخفیف در سشن
                request.session['coupon_discount'] = coupon_discount
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

    # محاسبه تخفیف نهایی
    total_discount = discount + coupon_discount

    shipping_cost = 0 if cart_total > 500000 else 25000
    tax = int((cart_total - total_discount) * 0.02) if (
                                                               cart_total - total_discount) > 0 else 0
    final_price = cart_total - total_discount + shipping_cost + tax

    available_count = sum(1 for item in cart_items if item.product.stock > 0)

    # محصولات پیشنهادی
    suggested_products = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=[item.product.id for item in cart_items]
    ).order_by('-created_at')[:5]

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'discount': total_discount,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'final_price': final_price,
        'available_count': available_count,
        'suggested_products': suggested_products,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
    }

    return render(request, 'cart/cart_detail.html', context)


@login_required
def add_to_cart_view(request, product_id):
    """افزودن محصول به سبد خرید"""

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)

    quantity = int(request.POST.get('quantity') or 1)

    if product.stock < quantity:
        messages.error(request, f'موجودی {product.name} کافی نیست.')
        return redirect(request.META.get('HTTP_REFERER', 'apps.products:product_list'))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity <= product.stock:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'تعداد {product.name} در سبد خرید افزایش یافت.')
        else:
            messages.error(request, f'موجودی {product.name} کافی نیست.')
    else:
        messages.success(request, f'{product.name} به سبد خرید اضافه شد.')

    return redirect(request.META.get('HTTP_REFERER', 'apps.cart:cart_detail'))


@login_required
def update_cart_item_view(request, item_id):
    """بروزرسانی تعداد آیتم سبد خرید"""

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
            messages.info(request, f'{cart_item.product.name} از سبد خرید حذف شد.')
        elif quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'سبد خرید بروزرسانی شد.')
        else:
            messages.error(request, f'موجودی {cart_item.product.name} کافی نیست.')

    return redirect('apps.cart:cart_detail')


@login_required
def remove_from_cart_view(request, item_id):
    """حذف آیتم از سبد خرید"""

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} از سبد خرید حذف شد.')

    return redirect('apps.cart:cart_detail')


@login_required
def move_to_wishlist_view(request, item_id):
    """انتقال آیتم از سبد خرید به علاقه‌مندی‌ها"""

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        from apps.products.models import Wishlist
        product = cart_item.product

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            messages.success(request, f'{product.name} به علاقه‌مندی‌ها اضافه شد.')
        else:
            messages.info(request, f'{product.name} قبلاً در علاقه‌مندی‌ها وجود دارد.')

        cart_item.delete()

    return redirect('apps.cart:cart_detail')


@login_required
def clear_cart_view(request):
    """خالی کردن کامل سبد خرید"""

    cart = get_or_create_cart(request.user)

    if request.method == 'POST':
        cart.items.all().delete()
        # حذف کوپن از سشن
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        if 'coupon_discount' in request.session:
            del request.session['coupon_discount']
        messages.info(request, 'سبد خرید شما خالی شد.')

    return redirect('apps.cart:cart_detail')


# ===== ویوهای کوپن =====

@login_required
def apply_coupon_view(request):
    """اعمال کد تخفیف در سبد خرید"""

    if request.method != 'POST':
        return redirect('apps.cart:cart_detail')

    coupon_code = request.POST.get('coupon_code', '').strip()

    if not coupon_code:
        messages.error(request, 'لطفاً کد تخفیف را وارد کنید.')
        return redirect('apps.cart:cart_detail')

    try:
        coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)

        # محاسبه مبلغ سبد خرید
        cart = get_or_create_cart(request.user)
        cart_total = int(cart.total_price) if cart.total_price else 0

        # بررسی اعتبار
        is_valid, message = coupon.is_valid(request.user, cart_total)

        if not is_valid:
            messages.error(request, f'❌ {message}')
            return redirect('apps.cart:cart_detail')

        # محاسبه تخفیف
        discount_amount = coupon.calculate_discount(cart_total)

        if discount_amount <= 0:
            messages.error(request, 'مبلغ تخفیف قابل اعمال نیست.')
            return redirect('apps.cart:cart_detail')

        # ذخیره در سشن
        request.session['coupon_id'] = coupon.id
        request.session['coupon_code'] = coupon.code
        request.session['coupon_discount'] = discount_amount

        messages.success(
            request,
            f'✅ کد تخفیف {coupon.code} با موفقیت اعمال شد. مبلغ تخفیف: {discount_amount:,.0f} تومان'
        )

    except Coupon.DoesNotExist:
        messages.error(request, '❌ کد تخفیف وارد شده معتبر نیست.')

    return redirect('apps.cart:cart_detail')


@login_required
def remove_coupon_view(request):
    """حذف کد تخفیف از سبد خرید"""

    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']

    messages.info(request, 'کد تخفیف با موفقیت حذف شد.')
    return redirect('apps.cart:cart_detail')
