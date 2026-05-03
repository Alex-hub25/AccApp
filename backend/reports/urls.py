from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('trial-balance/', views.trial_balance, name='trial_balance'),
    path('profit-loss/', views.profit_and_loss, name='profit_and_loss'),
    path('balance-sheet/', views.balance_sheet, name='balance_sheet'),
]
