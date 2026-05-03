from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from core.mixins import CompanyRequiredMixin
from .models import Expense
from .forms import ExpenseForm


class ExpenseListView(CompanyRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        qs = Expense.objects.filter(company=self.get_company()).select_related('account', 'contact')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(description__icontains=q)
        return qs

    def get_template_names(self):
        if self.request.htmx:
            return ['expenses/partials/expense_table.html']
        return [self.template_name]


class ExpenseDetailView(CompanyRequiredMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'

    def get_queryset(self):
        return Expense.objects.filter(company=self.get_company())


@login_required
def expense_create(request):
    company = request.user.profile.active_company if hasattr(request.user, 'profile') else None
    if not company:
        return redirect('accounts:company_list')
    if request.method == 'POST':
        form = ExpenseForm(company, request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.company = company
            expense.save()
            messages.success(request, 'Expense saved.')
            return redirect('expenses:list')
    else:
        form = ExpenseForm(company)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'New Expense'})


class ExpenseUpdateView(CompanyRequiredMixin, UpdateView):
    model = Expense
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')

    def get_queryset(self):
        return Expense.objects.filter(company=self.get_company())

    def get_form(self):
        return ExpenseForm(self.get_company(), **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(self.request, 'Expense updated.')
        return super().form_valid(form)


class ExpenseDeleteView(CompanyRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses:list')

    def get_queryset(self):
        return Expense.objects.filter(company=self.get_company())
