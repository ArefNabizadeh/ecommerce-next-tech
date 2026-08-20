# apps/orders/forms.py
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """فرم تسویه حساب - فقط برای یادداشت سفارش"""

    class Meta:
        model = Order
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 text-sm outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:bg-slate-900/50 dark:border-slate-700 dark:text-white',
                'rows': 3,
                'placeholder': 'نکات ویژه برای ارسال (اختیاری)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].required = False
        self.fields['note'].label = 'یادداشت سفارش'