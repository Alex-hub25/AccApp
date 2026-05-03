from django.urls import path
from . import views

app_name = 'taxes'

urlpatterns = [
    path('', views.TaxRateListView.as_view(), name='list'),
    path('new/', views.TaxRateCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TaxRateUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaxRateDeleteView.as_view(), name='delete'),
]
