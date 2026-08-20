# apps/products/forms.py
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """فرم ثبت نظر برای محصولات"""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 text-sm outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:bg-slate-900/50 dark:border-slate-700 dark:text-white dark:placeholder:text-slate-500',
                'rows': 4,
                'placeholder': 'نظر خود را درباره این محصول بنویسید...'
            }),
        }
        labels = {
            'rating': 'امتیاز شما',
            'comment': 'متن نظر',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = True
        self.fields['comment'].required = True