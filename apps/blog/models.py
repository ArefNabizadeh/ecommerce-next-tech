# apps/blog/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


class Category(models.Model):
    """مدل دسته‌بندی مقالات"""

    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            verbose_name="نامک")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="آیکون (Lucide)",
        help_text="نام آیکون از Lucide Icons مثل 'folder', 'smartphone', 'laptop'"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def article_count(self):
        return self.articles.filter(status='published').count()

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """مدل برچسب‌های مقالات"""

    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")
    slug = models.SlugField(max_length=60, unique=True, blank=True, verbose_name="نامک")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    """مدل مقاله"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'پیش‌نویس'
        PUBLISHED = 'published', 'منتشر شده'
        ARCHIVED = 'archived', 'بایگانی شده'

    # ===== فیلدهای اصلی =====
    title = models.CharField(max_length=250, verbose_name="عنوان مقاله")
    slug = models.SlugField(max_length=280, unique=True, blank=True,
                            verbose_name="نامک")
    content = models.TextField(verbose_name="محتوا")
    excerpt = models.TextField(
        blank=True,
        null=True,
        verbose_name="خلاصه",
        help_text="اگر خالی باشد، از ابتدای محتوا گرفته می‌شود"
    )

    # ===== روابط =====
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name="دسته‌بندی"
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        verbose_name="برچسب‌ها"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name="نویسنده"
    )

    # ===== تصویر =====
    image = models.ImageField(
        upload_to='blog/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="تصویر شاخص"
    )

    # ===== وضعیت =====
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت"
    )
    is_featured = models.BooleanField(default=False, verbose_name="مقاله ویژه")
    is_pinned = models.BooleanField(default=False, verbose_name="چسبیده")

    # ===== آمار =====
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    reading_time = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="زمان مطالعه (دقیقه)",
        help_text="زمان تقریبی مطالعه بر اساس تعداد کلمات"
    )

    # ===== تاریخ‌ها =====
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ انتشار"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # محاسبه زمان مطالعه (هر ۲۰۰ کلمه = ۱ دقیقه)
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))

        # اگر مقاله منتشر شد و published_at خالی است
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == 'published'
