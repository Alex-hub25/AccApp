from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_type', 'email', 'company', 'is_active']
    list_filter = ['contact_type', 'company']
