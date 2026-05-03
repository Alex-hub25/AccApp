from django.contrib import admin
from .models import TaxRate


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'company', 'is_active']
