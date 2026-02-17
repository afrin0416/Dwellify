from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'username', 'role', 'is_email_verified',
        'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_email_verified', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'role', 'is_email_verified', 'phone_number',
                'address', 'profile_picture'
            )
        }),
    )