# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegistrationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('apps.core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # messages.success(request, f'خوش آمدید {user.username} 👋')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('apps.core:home')
        else:
            # ✅ ارسال خطاهای دقیق به messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        # ترجمه خطاهای فیلدها به فارسی
                        field_names = {
                            'username': 'نام کاربری',
                            'password': 'رمز عبور',
                            'email': 'ایمیل',
                            'phone': 'شماره تلفن',
                            'first_name': 'نام',
                            'last_name': 'نام خانوادگی'
                        }
                        field_name = field_names.get(field, field)
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('apps.core:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'خوش آمدید {user.username}! 🎉')
            return redirect('apps.core:home')
        else:
            # ✅ ارسال خطاهای دقیق به messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_names = {
                            'username': 'نام کاربری',
                            'password': 'رمز عبور',
                            'password1': 'رمز عبور',
                            'password2': 'تکرار رمز عبور',
                            'email': 'ایمیل',
                            'phone': 'شماره تلفن',
                            'first_name': 'نام',
                            'last_name': 'نام خانوادگی'
                        }
                        field_name = field_names.get(field, field)
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'شما با موفقیت خارج شدید')
    return redirect('apps.core:home')
