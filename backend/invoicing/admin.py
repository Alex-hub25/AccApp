from django.contrib import admin
from .models import Invoice, InvoiceItem, Bill, BillItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'contact', 'date', 'status', 'company']
    inlines = [InvoiceItemInline]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['pk', 'contact', 'date', 'status', 'company']
    inlines = [BillItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'payment_type', 'contact', 'amount', 'date']
