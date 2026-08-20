from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, Address,UserActivity


# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone']

    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات اضافی', {'fields': ('phone', 'avatar')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'national_code', 'gender']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipient_name', 'province', 'city', 'is_default']
    list_filter = ['is_default', 'province']
    search_fields = ['user__username', 'recipient_name', 'city']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'message', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at', 'ip_address']
