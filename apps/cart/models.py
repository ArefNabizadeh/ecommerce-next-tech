from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

# Create your models here.

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='cart',
        verbose_name="کاربر")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    @property
    def total_price(self):
        total = sum(item.total_price for item in self.items.all())
        return total


    @property
    def total_discount(self):
        total = sum(item.discount_amount for item in self.items.all())
        return total

    @property
    def total_items(self):  # ← این رو اضافه کن
        """تعداد آیتم‌های سبد خرید"""
        return self.items.count()

    def __str__(self):
        return f"سبد خرید {self.user.username}"



class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items',verbose_name="سبد خرید")

    product = models.ForeignKey( Product,
        on_delete=models.CASCADE,
        verbose_name="محصول")

    quantity = models.PositiveIntegerField(default=1,verbose_name="تعداد")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ['cart', 'product']


    @property
    def total_price(self):
        """قیمت کل آیتم"""
        return self.product.final_price * self.quantity

    @property
    def discount_amount(self):
        """مبلغ تخفیف این آیتم"""
        if self.product.discount_price:
            return (self.product.price - self.product.discount_price) * self.quantity
        return 0

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"