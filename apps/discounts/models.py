# apps/discounts/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Coupon(models.Model):
    """مدل کد تخفیف"""

    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'درصدی'
        FIXED = 'fixed', 'مبلغ ثابت'

    # ===== اطلاعات اصلی =====
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تخفیف",
        help_text="کد تخفیف را با حروف بزرگ وارد کنید"
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT,
        verbose_name="نوع تخفیف"
    )
    discount_value = models.PositiveIntegerField(
        verbose_name="مقدار تخفیف",
        help_text="مثلاً ۲۰ برای ۲۰٪ یا ۵۰۰۰۰ برای ۵۰,۰۰۰ تومان"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )

    # ===== محدودیت‌ها =====
    min_order_amount = models.PositiveIntegerField(
        default=0,
        verbose_name="حداقل مبلغ سفارش",
        help_text="حداقل مبلغی که این کد قابل استفاده است"
    )
    max_discount_amount = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر تخفیف",
        help_text="حداکثر مبلغ تخفیف (فقط برای درصدی)"
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="تعداد استفاده مجاز",
        help_text="تعداد دفعاتی که این کد قابل استفاده است"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد استفاده شده"
    )
    used_by = models.ManyToManyField(
        User,
        blank=True,
        related_name='used_coupons',
        verbose_name="کاربران استفاده‌کننده"
    )

    # ===== وضعیت =====
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="عمومی",
        help_text="آیا این کد برای همه کاربران قابل استفاده است؟"
    )

    # ===== تاریخ‌ها =====
    valid_from = models.DateTimeField(
        default=timezone.now,
        verbose_name="شروع اعتبار"
    )
    valid_to = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="پایان اعتبار"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_from', 'valid_to']),
        ]

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else ' تومان'}"

    def clean(self):
        """اعتبارسنجی مدل"""
        if self.discount_type == 'percent' and self.discount_value > 100:
            raise ValidationError(
                {'discount_value': 'درصد تخفیف نمی‌تواند بیشتر از ۱۰۰ باشد.'})

        if self.valid_to and self.valid_to <= self.valid_from:
            raise ValidationError(
                {'valid_to': 'تاریخ پایان باید بعد از تاریخ شروع باشد.'})

    def is_valid(self, user=None, cart_total=0):
        """بررسی اعتبار کد"""
        now = timezone.now()

        # بررسی فعال بودن
        if not self.is_active:
            return False, "کد تخفیف غیرفعال است."

        # بررسی تاریخ اعتبار
        if now < self.valid_from:
            return False, f"کد تخفیف از {self.valid_from} فعال می‌شود."

        if self.valid_to and now > self.valid_to:
            return False, "کد تخفیف منقضی شده است."

        # بررسی تعداد استفاده
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "تعداد استفاده از این کد به پایان رسیده است."

        # بررسی حداقل مبلغ
        if cart_total < self.min_order_amount:
            return False, f"حداقل مبلغ سفارش برای این کد {self.min_order_amount:,.0f} تومان است."

        # بررسی اینکه کاربر قبلاً استفاده نکرده باشه
        if user and not self.is_public and self.used_by.filter(id=user.id).exists():
            return False, "شما قبلاً از این کد تخفیف استفاده کرده‌اید."

        return True, "کد تخفیف معتبر است."

    def calculate_discount(self, amount):
        """محاسبه مبلغ تخفیف"""
        if not amount:
            return 0

        if self.discount_type == self.DiscountType.PERCENT:
            discount = int((amount * self.discount_value) / 100)
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
        else:  # FIXED
            discount = self.discount_value

        # تخفیف نباید از مبلغ کل بیشتر بشه
        return min(discount, amount)

    def use_coupon(self, user):
        """استفاده از کد تخفیف"""
        if user:
            self.used_by.add(user)
        self.used_count += 1
        self.save()

    def save(self, *args, **kwargs):
        """ذخیره با اعتبارسنجی"""
        self.code = self.code.upper().strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def get_status(self):
        """دریافت وضعیت کوپن برای نمایش"""
        is_valid, message = self.is_valid()
        if is_valid:
            return 'active', 'فعال'
        return 'inactive', message