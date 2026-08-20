# apps/products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, Case, When, F, DecimalField
from .models import Product, Category, Brand, Wishlist, Review
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
def product_list_view(request):
    """صفحه لیست محصولات"""

    products = Product.objects.filter(is_active=True).select_related('category',
                                                                     'brand')
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    # ===== جستجو =====
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )

    # ===== فیلتر دسته‌بندی =====
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # ===== فیلتر برند (چندتایی) =====
    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)

    # ===== فیلتر محدوده قیمت (با قیمت نهایی) =====
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price or max_price:
        products = products.annotate(
            effective_price=Case(
                When(discount_price__isnull=False, then=F('discount_price')),
                default=F('price'),
                output_field=DecimalField()
            )
        )

        if min_price:
            try:
                min_price = int(min_price)
                products = products.filter(effective_price__gte=min_price)
            except ValueError:
                pass

        if max_price:
            try:
                max_price = int(max_price)
                products = products.filter(effective_price__lte=max_price)
            except ValueError:
                pass

    # ===== فیلتر موجودی =====
    if request.GET.get('in_stock') == 'true':
        products = products.filter(stock__gt=0)

    # ===== فیلتر تخفیف =====
    if request.GET.get('has_discount') == 'true':
        products = products.filter(discount_price__isnull=False)

    # ===== فیلتر گارانتی =====
    if request.GET.get('has_warranty') == 'true':
        products = products.filter(warranty__isnull=False).exclude(warranty='')

    # ===== مرتب‌سازی =====
    sort_by = request.GET.get('sort', '-created_at')

    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == '-name':
        products = products.order_by('-name')
    elif sort_by == '-rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')

    # ===== صفحه‌بندی =====
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ===== دسته‌بندی‌ها و برندها =====
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    # ===== ساخت query_params برای صفحه‌بندی =====
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_brands': brand_slugs,
        'sort_by': sort_by,
        'query_params': query_params.urlencode(),
        'wishlist_product_ids': wishlist_product_ids,
    }

    return render(request, 'products/product_list.html', context)


def product_detail_view(request, product_id, slug=None):
    """صفحه جزئیات محصول"""

    product = get_object_or_404(Product, id=product_id, is_active=True)

    # ===== افزایش بازدید =====
    product.views += 1
    product.save(update_fields=['views'])

    # ===== گالری =====
    gallery = product.images.all()

    # ===== مشخصات فنی =====
    specifications = product.specifications.all()

    # ===== نظرات (فقط تایید شده‌ها) =====
    reviews = product.reviews.filter(is_approved=True)
    reviews_count = reviews.count()

    # ===== محاسبه میانگین امتیاز =====
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    # ===== بررسی اینکه کاربر نظر داده یا نه =====
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()

    # ===== محصولات مرتبط =====
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).order_by('-created_at')[:4]

    # ===== محصولات اخیراً مشاهده شده =====
    recent_ids = request.session.get('recent_products', [])
    recent_products = Product.objects.filter(
        id__in=recent_ids,
        is_active=True
    )[:5] if recent_ids else []

    # ===== اضافه کردن به سشن =====
    if product.id not in recent_ids:
        recent_ids.insert(0, product.id)
        if len(recent_ids) > 10:
            recent_ids = recent_ids[:10]
        request.session['recent_products'] = recent_ids

    context = {
        'product': product,
        'gallery': gallery,
        'specifications': specifications,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'related_products': related_products,
        'recent_products': recent_products,
    }

    return render(request, 'products/product_detail.html', context)


def category_list_view(request):
    """صفحه لیست دسته‌بندی‌ها"""

    categories = Category.objects.filter(is_active=True)

    # ===== جستجو =====
    search_query = request.GET.get('q')
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    # ===== دسته‌بندی‌های ویژه =====
    featured_categories = categories.filter(is_featured=True)[:5]

    # ===== دسته‌بندی‌های محبوب =====
    popular_categories = categories.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('-product_count')[:6]

    context = {
        'categories': categories,
        'featured_categories': featured_categories,
        'popular_categories': popular_categories,
        'search_query': search_query,
    }

    return render(request, 'products/category_list.html', context)


def brand_list_view(request):
    """صفحه لیست برندها"""

    brands = Brand.objects.filter(is_active=True)

    # ===== جستجو =====
    search_query = request.GET.get('q')
    if search_query:
        brands = brands.filter(name__icontains=search_query)

    # ===== فیلتر الفبا =====
    letter = request.GET.get('letter')
    if letter:
        brands = brands.filter(name__startswith=letter)

    # ===== برندهای ویژه =====
    featured_brands = brands.filter(is_featured=True)[:5]

    # ===== برندهای محبوب =====
    popular_brands = brands.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('-product_count')[:6]

    context = {
        'brands': brands,
        'featured_brands': featured_brands,
        'popular_brands': popular_brands,
        'search_query': search_query,
        'selected_letter': letter,
    }

    return render(request, 'products/brand_list.html', context)


@login_required
def add_to_wishlist_view(request, product_id):
    """افزودن محصول به علاقه‌مندی‌ها"""

    product = get_object_or_404(Product, id=product_id, is_active=True)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, f'{product.name} به علاقه‌مندی‌ها اضافه شد ❤️')
    else:
        messages.info(request, f'{product.name} قبلاً در علاقه‌مندی‌ها وجود دارد.')

    return redirect(request.META.get('HTTP_REFERER', 'apps.products:product_list'))


@login_required
def remove_from_wishlist_view(request, product_id):
    """حذف محصول از علاقه‌مندی‌ها"""

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f'{product.name} از علاقه‌مندی‌ها حذف شد.')

    return redirect(request.META.get('HTTP_REFERER', 'apps.products:product_list'))


def search_api(request):
    """API جستجوی محصولات برای نوار ناوبری"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(brand__name__icontains=query),
        is_active=True
    ).select_related('category','brand')[:10]

    results = []
    for product in products:
        final_price = product.final_price
        results.append({
            'id': product.id,
            'name': product.name,
            'price': float(final_price),
            'category': product.category.name if product.category else '',
            'brand': (
                product.brand.name
                if product.brand
                else ''
            ),
            'image': (
                product.image.url
                if product.image
                else None
            ),

            'url': reverse(
                'apps.products:product_detail',
                kwargs={
                    'slug': product.slug
                }
            ),
        })

    return JsonResponse({'results': results})