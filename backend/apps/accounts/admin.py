from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'school_name', 'district']
    list_filter = ['role', 'district']
    search_fields = ['username', 'email', 'first_name', 'last_name']
