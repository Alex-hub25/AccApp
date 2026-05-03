from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required

from core.mixins import CompanyRequiredMixin
from .models import Account, JournalEntry, JournalEntryLine
from .forms import AccountForm, JournalEntryForm, get_line_formset


# ─── Accounts ────────────────────────────────────────────────────────────────

class AccountListView(CompanyRequiredMixin, ListView):
    model = Account
    template_name = 'ledger/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        qs = Account.objects.filter(company=self.get_company())
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        return qs

    def get_template_names(self):
        if self.request.htmx:
            return ['ledger/partials/account_table.html']
        return [self.template_name]


class AccountCreateView(CompanyRequiredMixin, CreateView):
    model = Account
    template_name = 'ledger/account_form.html'
    success_url = reverse_lazy('ledger:account_list')

    def get_form(self):
        return AccountForm(self.get_company(), **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.company = self.get_company()
        messages.success(self.request, 'Account created.')
        return super().form_valid(form)


class AccountUpdateView(CompanyRequiredMixin, UpdateView):
    model = Account
    template_name = 'ledger/account_form.html'
    success_url = reverse_lazy('ledger:account_list')

    def get_queryset(self):
        return Account.objects.filter(company=self.get_company())

    def get_form(self):
        return AccountForm(self.get_company(), **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(self.request, 'Account updated.')
        return super().form_valid(form)


class AccountDetailView(CompanyRequiredMixin, DetailView):
    model = Account
    template_name = 'ledger/account_detail.html'

    def get_queryset(self):
        return Account.objects.filter(company=self.get_company())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lines = JournalEntryLine.objects.filter(
            account=self.object, entry__is_posted=True
        ).select_related('entry').order_by('entry__date')
        ctx['lines'] = lines
        return ctx


# ─── Journal Entries ──────────────────────────────────────────────────────────

class JournalEntryListView(CompanyRequiredMixin, ListView):
    model = JournalEntry
    template_name = 'ledger/entry_list.html'
    context_object_name = 'entries'

    def get_queryset(self):
        return JournalEntry.objects.filter(company=self.get_company()).prefetch_related('lines')


@login_required
def journal_entry_create(request):
    from core.mixins import CompanyRequiredMixin
    if not hasattr(request.user, 'profile') or not request.user.profile.active_company:
        messages.warning(request, 'Please select a company first.')
        return redirect('accounts:company_list')
    company = request.user.profile.active_company
    LineFormSet = get_line_formset(company, extra=3)

    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        formset = LineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            entry = form.save(commit=False)
            entry.company = company
            entry.save()
            formset.instance = entry
            formset.save()
            messages.success(request, f'Journal entry {entry} saved.')
            return redirect('ledger:entry_list')
    else:
        form = JournalEntryForm()
        formset = LineFormSet()

    return render(request, 'ledger/entry_form.html', {
        'form': form, 'formset': formset, 'title': 'New Journal Entry',
    })


@login_required
def journal_entry_edit(request, pk):
    if not hasattr(request.user, 'profile') or not request.user.profile.active_company:
        return redirect('accounts:company_list')
    company = request.user.profile.active_company
    entry = get_object_or_404(JournalEntry, pk=pk, company=company)
    LineFormSet = get_line_formset(company, extra=1)

    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        formset = LineFormSet(request.POST, instance=entry)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Journal entry updated.')
            return redirect('ledger:entry_list')
    else:
        form = JournalEntryForm(instance=entry)
        formset = LineFormSet(instance=entry)

    return render(request, 'ledger/entry_form.html', {
        'form': form, 'formset': formset, 'entry': entry, 'title': 'Edit Journal Entry',
    })


@login_required
def journal_entry_post(request, pk):
    if not hasattr(request.user, 'profile') or not request.user.profile.active_company:
        return redirect('accounts:company_list')
    company = request.user.profile.active_company
    entry = get_object_or_404(JournalEntry, pk=pk, company=company)
    if request.method == 'POST':
        # Validate balance before posting
        if entry.total_debit != entry.total_credit:
            messages.error(request, 'Cannot post: debits do not equal credits.')
        else:
            entry.is_posted = not entry.is_posted
            entry.save()
            status = 'posted' if entry.is_posted else 'unposted'
            messages.success(request, f'Entry {status}.')
    return redirect('ledger:entry_list')
