from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


# ==========================================
# User
# ==========================================

class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="شماره تلفن باید با 09 شروع شود و 11 رقم باشد"
    )

    phone = models.CharField(
        max_length=11,
        validators=[phone_regex],
        blank=True,
        null=True,
        verbose_name="شماره تلفن"
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='آدرس'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ('-date_joined',)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username


# ==========================================
# Profile
# ==========================================

class Profile(models.Model):
    GENDER_CHOICES = (
        ('male', 'مرد'),
        ('female', 'زن'),
        ('other', 'سایر'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="کاربر"
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="شماره تلفن",
        validators=[
            RegexValidator(
                r'^09\d{9}$',
                'شماره تلفن معتبر نیست'
            )
        ]
    )

    national_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="کد ملی",
        validators=[
            RegexValidator(
                r'^\d{10}$',
                'کد ملی باید ۱۰ رقم باشد'
            )
        ]
    )

    birth_date = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="تاریخ تولد"
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="جنسیت"
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return f"پروفایل {self.user.username}"


# ==========================================
# Address
# ==========================================

class Address(models.Model):
    """آدرس‌های کاربر"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="کاربر"
    )

    recipient_name = models.CharField(
        max_length=100,
        verbose_name="نام گیرنده"
    )

    phone = models.CharField(
        max_length=11,
        verbose_name="شماره تلفن"
    )

    province = models.CharField(
        max_length=50,
        verbose_name="استان"
    )

    city = models.CharField(
        max_length=50,
        verbose_name="شهر"
    )

    street_address = models.TextField(
        verbose_name="آدرس"
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="کد پستی"
    )

    unit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="واحد"
    )

    delivery_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت تحویل"
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="آدرس پیش‌فرض"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.recipient_name} - {self.province} {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(
                id=self.id
            ).update(
                is_default=False
            )

        super().save(*args, **kwargs)


# ==========================================
# User Activity
# ==========================================

class UserActivity(models.Model):
    """مدل فعالیت‌های کاربر"""

    class ActivityType(models.TextChoices):

        ORDER_CREATED = 'order_created', 'سفارش جدید'
        ORDER_PAID = 'order_paid', 'پرداخت سفارش'
        ORDER_COMPLETED = 'order_completed', 'تکمیل سفارش'
        ORDER_CANCELLED = 'order_cancelled', 'لغو سفارش'
        WISHLIST_ADDED = 'wishlist_added', 'افزودن به علاقه‌مندی'
        WISHLIST_REMOVED = 'wishlist_removed', 'حذف از علاقه‌مندی'
        ADDRESS_ADDED = 'address_added', 'افزودن آدرس'
        ADDRESS_UPDATED = 'address_updated', 'ویرایش آدرس'
        PROFILE_UPDATED = 'profile_updated', 'ویرایش پروفایل'
        REVIEW_ADDED = 'review_added', 'ثبت نظر'
        LOGIN = 'login', 'ورود به حساب'
        LOGOUT = 'logout', 'خروج از حساب'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="کاربر"
    )

    type = models.CharField(
        max_length=50,
        choices=ActivityType.choices,
        verbose_name="نوع فعالیت"
    )

    message = models.CharField(
        max_length=255,
        verbose_name="پیام فعالیت"
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="آیکون"
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="داده‌های اضافی"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="آدرس IP"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "فعالیت کاربر"
        verbose_name_plural = "فعالیت‌های کاربران"
        ordering = ['-created_at']

        indexes = [
            models.Index(
                fields=['user', 'created_at']
            ),
            models.Index(
                fields=['type']
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.get_type_display()} - "
            f"{self.created_at}"
        )

    @classmethod
    def log_activity(
            cls,
            user,
            activity_type,
            message,
            icon=None,
            metadata=None,
            request=None
    ):
        """ثبت فعالیت جدید"""

        ip = None

        if request:
            x_forwarded_for = request.META.get(
                'HTTP_X_FORWARDED_FOR'
            )

            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get(
                    'REMOTE_ADDR'
                )

        return cls.objects.create(
            user=user,
            type=activity_type,
            message=message,
            icon=icon or cls.get_icon_for_type(activity_type),
            metadata=metadata or {},
            ip_address=ip
        )

    @staticmethod
    def get_icon_for_type(activity_type):
        """دریافت آیکون بر اساس نوع فعالیت"""

        icons = {
            'order_created': 'shopping-bag',
            'order_paid': 'credit-card',
            'order_completed': 'check-circle',
            'order_cancelled': 'x-circle',
            'wishlist_added': 'heart',
            'wishlist_removed': 'heart-off',
            'address_added': 'map-pin',
            'address_updated': 'edit',
            'profile_updated': 'user',
            'review_added': 'star',
            'login': 'log-in',
            'logout': 'log-out',
        }

        return icons.get(
            activity_type,
            'activity'
        )
