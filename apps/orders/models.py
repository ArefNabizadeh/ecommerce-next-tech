# apps/orders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.products.models import Product


User = get_user_model()

class Order(models.Model):
    """مدل سفارشات"""

    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده'
        PROCESSING = 'processing', 'در حال پردازش'
        SHIPPED = 'shipped', 'ارسال شده'
        DELIVERED = 'delivered', 'تحویل داده شده'
        CANCELLED = 'cancelled', 'لغو شده'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده'
        FAILED = 'failed', 'ناموفق'
        REFUNDED = 'refunded', 'بازگشت وجه'

    class PaymentMethod(models.TextChoices):
        ONLINE = 'online', 'پرداخت آنلاین'
        WALLET = 'wallet', 'کیف پول'
        CASH = 'cash', 'پرداخت در محل'

    class ShippingMethod(models.TextChoices):
        STANDARD = 'standard', 'ارسال عادی'
        EXPRESS = 'express', 'ارسال فوری'
        PREMIUM = 'premium', 'ارسال ویژه'

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="کاربر"
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="شماره سفارش"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="قیمت کل"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="جمع کل (بدون تخفیف)"
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="تخفیف"
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="هزینه ارسال"
    )
    tax = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="مالیات"
    )

    address = models.TextField(verbose_name="آدرس تحویل")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="وضعیت سفارش"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="وضعیت پرداخت"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE,
        verbose_name="روش پرداخت"
    )
    shipping_method = models.CharField(
        max_length=20,
        choices=ShippingMethod.choices,
        default=ShippingMethod.STANDARD,
        verbose_name="روش ارسال"
    )

    tracking_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="کد رهگیری"
    )
    note = models.TextField(blank=True, null=True, verbose_name="یادداشت")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(
                order_number__startswith=f'ORD-{date_str}'
            ).order_by('-order_number').first()

            if last_order:
                last_num = int(last_order.order_number.split('-')[-1]) + 1
            else:
                last_num = 1

            self.order_number = f'ORD-{date_str}-{last_num:04d}'
        super().save(*args, **kwargs)

    @property
    def items_count(self):
        """تعداد آیتم‌های سفارش"""
        return self.items.count()

    @property
    def expected_delivery(self):
        """محاسبه زمان تحویل بر اساس روش ارسال"""
        if self.shipping_method == self.ShippingMethod.STANDARD:
            return "۳-۵ روز"
        elif self.shipping_method == self.ShippingMethod.EXPRESS:
            return "۲۴ ساعت"
        elif self.shipping_method == self.ShippingMethod.PREMIUM:
            return "۶-۱۲ ساعت"
        return "۳-۵ روز"

    @property
    def shipping_cost_display(self):
        """نمایش هزینه ارسال با فرمت تومان"""
        return f"{self.shipping_cost:,.0f} تومان"

    def __str__(self):
        return f"سفارش #{self.order_number}"


class OrderItem(models.Model):
    """مدل آیتم‌های سفارش"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سفارش"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="محصول"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,  # ✅ مقدار پیش‌فرض اضافه شد
        verbose_name="قیمت واحد"
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    @property
    def total_price(self):
        """قیمت کل آیتم سفارش"""
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"