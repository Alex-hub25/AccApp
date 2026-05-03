from django.contrib import admin
from .models import Account, JournalEntry, JournalEntryLine


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'company', 'is_active']
    list_filter = ['account_type', 'company']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'date', 'description', 'is_posted', 'company']
    inlines = [JournalEntryLineInline]
