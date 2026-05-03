from django.urls import path
from . import views

app_name = 'invoicing'

urlpatterns = [
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    # Bills
    path('bills/', views.BillListView.as_view(), name='bill_list'),
    path('bills/new/', views.bill_create, name='bill_create'),
    path('bills/<int:pk>/', views.BillDetailView.as_view(), name='bill_detail'),
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('payments/new/invoice/<int:invoice_pk>/', views.payment_create, name='payment_for_invoice'),
    path('payments/new/bill/<int:bill_pk>/', views.payment_create, name='payment_for_bill'),
]
