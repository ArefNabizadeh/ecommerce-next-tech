# apps/products/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام برند")

    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            verbose_name='نامک')

    logo = models.ImageField(upload_to='brands/', blank=True, null=True,
                             verbose_name="لوگو")

    country = models.CharField(max_length=100, blank=True, null=True,
                               verbose_name="کشور")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    is_featured = models.BooleanField(default=False, verbose_name="ویژه")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def products_count(self):
        return self.products.filter(is_active=True).count()

    def __str__(self):
        return self.name


class Category(models.Model):
    """مدل دسته‌بندی محصولات"""

    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            verbose_name="نامک")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to='categories/', blank=True, null=True,
                              verbose_name="تصویر")
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="آیکون (Lucide)",
        help_text="نام آیکون از Lucide Icons"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def products_count(self):
        return self.products.filter(is_active=True).count()

    def __str__(self):
        return self.name


class Product(models.Model):
    """مدل محصولات فروشگاه"""

    # ===== روابط =====
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='products',
        blank=True,
        null=True,
        verbose_name="برند"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="دسته‌بندی"
    )

    # ===== اطلاعات اصلی =====
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=220, unique=True, blank=True,
                            verbose_name="نامک")
    description = models.TextField(verbose_name="توضیحات")

    # ===== قیمت و موجودی =====
    price = models.DecimalField(max_digits=12, decimal_places=0,
                                verbose_name="قیمت (تومان)")
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name="قیمت تخفیف‌خورده"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")

    # ===== مشخصات =====
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="رنگ")
    warranty = models.CharField(max_length=100, blank=True, null=True,
                                verbose_name="گارانتی")

    # ===== تصویر =====
    image = models.ImageField(upload_to='products/', blank=True, null=True,
                              verbose_name="تصویر اصلی")

    # ===== وضعیت =====
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="محصول ویژه")

    # ===== آمار =====
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def get_discount_percent(self):
        if self.discount_price and self.price and self.discount_price < self.price:
            return round(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def average_rating(self):
        from django.db.models import Avg
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def reviews_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """تصاویر اضافی محصول"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="محصول"
    )
    image = models.ImageField(upload_to='products/gallery/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name="متن جایگزین")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"تصویر {self.product.name} - {self.id}"


class ProductSpecification(models.Model):
    """مشخصات فنی محصولات"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name="محصول"
    )
    key = models.CharField(max_length=100, verbose_name="عنوان مشخصه")
    value = models.CharField(max_length=200, verbose_name="مقدار مشخصه")

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"
        ordering = ['key']

    def __str__(self):
        return f"{self.key}: {self.value}"


class Review(models.Model):
    """نظرات و امتیازات محصولات"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="محصول"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="کاربر"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="سفارش مرتبط",
        null=True,
        blank=True
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="امتیاز"
    )
    comment = models.TextField(verbose_name="نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"


class Wishlist(models.Model):
    """علاقه‌مندی‌های کاربر"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name="کاربر"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name="محصول"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        ordering = ['-created_at']
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class FlashSale(models.Model):
    """مدل فروش ویژه"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    hours = models.PositiveSmallIntegerField(default=12, verbose_name="ساعت")
    minutes = models.PositiveSmallIntegerField(default=0, verbose_name="دقیقه")
    seconds = models.PositiveSmallIntegerField(default=0, verbose_name="ثانیه")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "فروش ویژه"
        verbose_name_plural = "فروش‌های ویژه"

    def __str__(self):
        return f"{self.title} - {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"