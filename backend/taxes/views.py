from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.mixins import CompanyRequiredMixin
from .models import TaxRate
from .forms import TaxRateForm


class TaxRateListView(CompanyRequiredMixin, ListView):
    model = TaxRate
    template_name = 'taxes/taxrate_list.html'
    context_object_name = 'tax_rates'

    def get_queryset(self):
        return TaxRate.objects.filter(company=self.get_company())


class TaxRateCreateView(CompanyRequiredMixin, CreateView):
    model = TaxRate
    form_class = TaxRateForm
    template_name = 'taxes/taxrate_form.html'
    success_url = reverse_lazy('taxes:list')

    def form_valid(self, form):
        form.instance.company = self.get_company()
        messages.success(self.request, 'Tax rate created.')
        return super().form_valid(form)


class TaxRateUpdateView(CompanyRequiredMixin, UpdateView):
    model = TaxRate
    form_class = TaxRateForm
    template_name = 'taxes/taxrate_form.html'
    success_url = reverse_lazy('taxes:list')

    def get_queryset(self):
        return TaxRate.objects.filter(company=self.get_company())

    def form_valid(self, form):
        messages.success(self.request, 'Tax rate updated.')
        return super().form_valid(form)


class TaxRateDeleteView(CompanyRequiredMixin, DeleteView):
    model = TaxRate
    template_name = 'taxes/taxrate_confirm_delete.html'
    success_url = reverse_lazy('taxes:list')

    def get_queryset(self):
        return TaxRate.objects.filter(company=self.get_company())
