from django import forms
from .models import Article, Category, Tag



class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'content', 'excerpt', 'image',
            'category', 'tags', 'status', 'is_featured', 'is_pinned'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'عنوان مقاله را وارد کنید'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'rows': 15,
                'placeholder': 'محتوای مقاله را وارد کنید...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'rows': 3,
                'placeholder': 'خلاصه مقاله (اختیاری)'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'size-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-200'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'size-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-200'
            }),
        }