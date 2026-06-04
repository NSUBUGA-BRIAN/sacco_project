from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'member_number', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'national_id', 'member_number')
    fieldsets = UserAdmin.fieldsets + (
        ('SACCO Info', {'fields': ('role', 'national_id', 'phone_number', 'address',
                                   'occupation', 'monthly_income', 'member_number', 'profile_photo')}),
    )
