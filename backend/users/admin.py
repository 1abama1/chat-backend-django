from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserStatus

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen']

