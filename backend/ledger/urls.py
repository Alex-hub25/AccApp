from django.urls import path
from . import views

app_name = 'ledger'

urlpatterns = [
    # Chart of Accounts
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/new/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_edit'),
    # Journal Entries
    path('entries/', views.JournalEntryListView.as_view(), name='entry_list'),
    path('entries/new/', views.journal_entry_create, name='entry_create'),
    path('entries/<int:pk>/edit/', views.journal_entry_edit, name='entry_edit'),
    path('entries/<int:pk>/post/', views.journal_entry_post, name='entry_post'),
]
