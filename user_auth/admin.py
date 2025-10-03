from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user_auth.forms import CustomUserCreationForm, CustomUserChangeForm
from user_auth.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = None
    list_display = ['email']
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = [
        ('Personal info', {
            'fields': ['email', 'bio','first_name','last_name','phone','address'],
        }),
        ('Permissions', {
            'fields': ["is_staff", "is_active", "groups", "user_permissions"]
        }),
    ]
    add_fieldsets = [
        ('Personal info', {
            'fields': ['email', 'bio','first_name','last_name','phone','address'],
        }),
        ('Permissions', {
            'fields': ["is_staff", "is_active", "groups", "user_permissions"]
        }),
    ]
