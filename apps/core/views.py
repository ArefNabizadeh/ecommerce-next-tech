from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
# Create your views here.


def home(request):
    context = {"brands" : [
    {'name': 'Apple', 'slug': 'apple', 'icon': 'apple.svg'},
    {'name': 'Samsung', 'slug': 'samsung', 'icon': 'samsung.svg'},
    {'name': 'Sony', 'slug': 'sony', 'icon': 'sony.svg'},
    {'name': 'Asus', 'slug': 'asus', 'icon': 'asus.svg'},
    {'name': 'MSI', 'slug': 'msi', 'icon': 'msi.svg'},
    {'name': 'HP', 'slug': 'hp', 'icon': 'hp.svg'},
    {'name': 'Dell', 'slug': 'dell', 'icon': 'dell.svg'},
    {'name': 'Lenovo', 'slug': 'lenovo', 'icon': 'lenovo.svg'},
    {'name': 'Acer', 'slug': 'acer', 'icon': 'acer.svg'},
    {'name': 'Intel', 'slug': 'intel', 'icon': 'intel.svg'},
    {'name': 'AMD', 'slug': 'amd', 'icon': 'amd.svg'},
    {'name': 'NVIDIA', 'slug': 'nvidia', 'icon': 'nvidia.svg'},

    {'name': 'JBL', 'slug': 'jbl', 'icon': 'jbl.svg'},
    {'name': 'Xiaomi', 'slug': 'xiaomi', 'icon': 'xiaomi.svg'},
]}
    return render(request, "home.html",context)

def error_404_preview(request):
    return render(request, "../templates/errors/404.html")

def error_500_preview(request):
    return render(request, "../templates/errors/500.html")

def clear_messages(request):
    """پاک کردن همه پیام‌های سشن"""
    storage = messages.get_messages(request)
    storage.used = True  # این باعث می‌شود پیام‌ها مصرف شده در نظر گرفته شوند
    return HttpResponse('OK')