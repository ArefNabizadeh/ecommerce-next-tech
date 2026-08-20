# apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, Profile, Address  # ← Profile و Address رو اضافه کن


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 pr-12 text-sm outline-none'}))
    phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(
        attrs={
            'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 pr-12 text-sm outline-none',
            'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1',
                  'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 pr-12 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='نام کاربری یا ایمیل',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
            'placeholder': 'نام کاربری یا ایمیل خود را وارد کنید'
        })
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full rounded-xl border bg-white/50 px-4 py-3 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
    )

    def clean(self):
        """اعتبارسنجی و احراز هویت با ایمیل یا نام کاربری"""
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = username_or_email

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    'نام کاربری، ایمیل یا رمز عبور اشتباه است.',
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


# ================================================
# ===== فرم‌های جدید برای داشبورد =====
# ================================================

class ProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""

    class Meta:
        model = Profile
        fields = ['phone', 'national_code', 'birth_date', 'gender','avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'
            }),
            'national_code': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'کد ملی ده رقمی'
            }),
            'birth_date': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': '۱۴۰۰/۰۱/۰۱'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'id': 'avatar-input',
                'accept': 'image/*'
            }),
        }


class AddressForm(forms.ModelForm):
    """فرم افزودن/ویرایش آدرس"""

    class Meta:
        model = Address
        fields = ['recipient_name', 'phone', 'province', 'city', 'street_address',
                  'postal_code', 'unit', 'delivery_notes', 'is_default']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'نام کامل گیرنده'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'
            }),
            'province': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'استان'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'شهر'
            }),
            'street_address': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'خیابان، پلاک، واحد...',
                'rows': '4'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'کد پستی ده رقمی'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'واحد (اختیاری)'
            }),
            'delivery_notes': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border bg-white/50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
                'placeholder': 'نکات ویژه برای تحویل (اختیاری)',
                'rows': '3'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'size-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-200'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['postal_code'].required = False
        self.fields['unit'].required = False
        self.fields['delivery_notes'].required = False
        self.fields['is_default'].required = False