# apps/blog/admin.py
from django.contrib import admin
from django.db.models import Count
from .models import Category, Tag, Article
from django.db.models import Q


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'article_count_display']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def article_count_display(self, obj):
        """تعداد مقالات این دسته‌بندی"""
        return obj.articles.filter(status='published').count()

    article_count_display.short_description = "تعداد مقالات"

    # اگر می‌خواهید با یک کوئری بهینه‌تر انجام شود:
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        )

    def article_count_display(self, obj):
        return getattr(obj, 'article_count', 0)

    article_count_display.short_description = "تعداد مقالات"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'author', 'status',
        'is_featured', 'is_pinned', 'views', 'reading_time',
        'published_at'
    ]
    list_filter = ['status', 'category', 'is_featured', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'reading_time', 'created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'image')
        }),
        ('دسته‌بندی و برچسب‌ها', {
            'fields': ('category', 'tags')
        }),
        ('نویسنده و وضعیت', {
            'fields': ('status', 'published_at', 'is_featured', 'is_pinned')
        }),
        ('آمار', {
            'fields': ('views', 'reading_time', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)