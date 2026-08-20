from django import forms


class CouponForm(forms.Form):
    """فرم اعمال کد تخفیف"""
    coupon_code = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'flex-1 rounded-xl border bg-white/50 px-3 py-2 text-sm outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:bg-slate-900/50 dark:border-slate-700 dark:text-white dark:placeholder:text-slate-500',
            'placeholder': 'کد تخفیف...'
        })
    )

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code', '').strip().upper()
        if not code:
            raise forms.ValidationError('لطفاً کد تخفیف را وارد کنید.')
        return code