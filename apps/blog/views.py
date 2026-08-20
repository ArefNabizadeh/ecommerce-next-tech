from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Sum
from django.utils import timezone
from .models import Article, Category, Tag


# Create your views here.


def blog_list_view(request):
    """صفحه لیست مقالات"""

    # ===== دریافت مقالات منتشر شده =====
    articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).select_related('category', 'author').prefetch_related('tags')

    # ===== فیلتر بر اساس دسته‌بندی =====
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    # ===== فیلتر بر اساس برچسب =====
    tag_slug = request.GET.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)

    # ===== جستجو =====
    search_query = request.GET.get('q')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )

    # ===== مرتب‌سازی =====
    sort_by = request.GET.get('sort', '-published_at')
    allowed_sorts = ['published_at', '-published_at', 'title', '-title', 'views',
                     '-views']
    if sort_by in allowed_sorts:
        articles = articles.order_by(sort_by)
    else:
        articles = articles.order_by('-published_at')

    # ===== مقاله ویژه =====
    featured_article = articles.filter(is_featured=True).first()

    # ===== دسته‌بندی‌ها با تعداد مقالات (✅ اصلاح شده) =====
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        article_count=Count('articles', filter=Q(articles__status='published')),
        views_count=Sum('articles__views')
    ).order_by('name')

    # ===== مقالات اخیر =====
    recent_articles = articles.order_by('-published_at')[:5]

    # ===== صفحه‌بندی =====
    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ===== پارامترهای query =====
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_params = query_params.urlencode()

    context = {
        'articles': page_obj,
        'featured_article': featured_article,
        'categories': categories,  # ← اینجا categories با article_count ارسال می‌شود
        'recent_articles': recent_articles,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'query_params': query_params,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
        'sort_by': sort_by,
    }

    return render(request, 'blog/blog_list.html', context)


def blog_detail_view(request, slug):
    """صفحه جزئیات مقاله"""

    article = get_object_or_404(
        Article,
        slug=slug,
        status='published',
        published_at__lte=timezone.now()
    )

    # ===== افزایش بازدید =====
    article.views += 1
    article.save(update_fields=['views'])

    # ===== مقالات قبلی و بعدی =====
    prev_article = Article.objects.filter(
        status='published',
        published_at__lt=article.published_at
    ).order_by('-published_at').first()

    next_article = Article.objects.filter(
        status='published',
        published_at__gt=article.published_at
    ).order_by('published_at').first()

    # ===== مقالات مرتبط =====
    related_articles = Article.objects.filter(
        status='published',
        category=article.category
    ).exclude(id=article.id).order_by('-published_at')[:3]

    context = {
        'article': article,
        'prev_article': prev_article,
        'next_article': next_article,
        'related_articles': related_articles,
    }

    return render(request, 'blog/blog_detail.html', context)


# apps/blog/views.py

def category_list_view(request):
    """صفحه لیست دسته‌بندی‌ها"""

    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        article_count=Count('articles', filter=Q(articles__status='published')),
        views_count=Sum('articles__views')
    ).order_by('name')

    # ===== جستجو =====
    search_query = request.GET.get('q')
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    # ===== صفحه‌بندی =====
    paginator = Paginator(categories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_params = query_params.urlencode()

    context = {
        'categories': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'query_params': query_params,
        'search_query': search_query,
    }

    return render(request, 'blog/category-list.html', context)
