from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from core.mixins import CompanyRequiredMixin
from .models import Invoice, Bill, Payment
from .forms import (
    InvoiceForm, get_invoice_item_formset,
    BillForm, get_bill_item_formset,
    PaymentForm,
)


# ─── Invoices ─────────────────────────────────────────────────────────────────

class InvoiceListView(CompanyRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoicing/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        qs = Invoice.objects.filter(company=self.get_company()).select_related('contact')
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_template_names(self):
        if self.request.htmx:
            return ['invoicing/partials/invoice_table.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Invoice.Status.choices
        return ctx


class InvoiceDetailView(CompanyRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoicing/invoice_detail.html'

    def get_queryset(self):
        return Invoice.objects.filter(company=self.get_company())


def _get_company(request):
    if hasattr(request.user, 'profile') and request.user.profile.active_company:
        return request.user.profile.active_company
    return None


@login_required
def invoice_create(request):
    company = _get_company(request)
    if not company:
        messages.warning(request, 'Select a company first.')
        return redirect('accounts:company_list')

    ItemFormSet = get_invoice_item_formset(company, extra=3)
    if request.method == 'POST':
        form = InvoiceForm(company, request.POST)
        formset = ItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.company = company
            invoice.save()
            formset.instance = invoice
            formset.save()
            messages.success(request, f'Invoice {invoice} created.')
            return redirect('invoicing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(company)
        formset = ItemFormSet()

    return render(request, 'invoicing/invoice_form.html', {
        'form': form, 'formset': formset, 'title': 'New Invoice',
    })


@login_required
def invoice_edit(request, pk):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')
    invoice = get_object_or_404(Invoice, pk=pk, company=company)
    ItemFormSet = get_invoice_item_formset(company, extra=1)

    if request.method == 'POST':
        form = InvoiceForm(company, request.POST, instance=invoice)
        formset = ItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Invoice updated.')
            return redirect('invoicing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(company, instance=invoice)
        formset = ItemFormSet(instance=invoice)

    return render(request, 'invoicing/invoice_form.html', {
        'form': form, 'formset': formset, 'invoice': invoice, 'title': 'Edit Invoice',
    })


# ─── Bills ────────────────────────────────────────────────────────────────────

class BillListView(CompanyRequiredMixin, ListView):
    model = Bill
    template_name = 'invoicing/bill_list.html'
    context_object_name = 'bills'

    def get_queryset(self):
        qs = Bill.objects.filter(company=self.get_company()).select_related('contact')
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs


class BillDetailView(CompanyRequiredMixin, DetailView):
    model = Bill
    template_name = 'invoicing/bill_detail.html'

    def get_queryset(self):
        return Bill.objects.filter(company=self.get_company())


@login_required
def bill_create(request):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')
    ItemFormSet = get_bill_item_formset(company, extra=3)

    if request.method == 'POST':
        form = BillForm(company, request.POST)
        formset = ItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            bill = form.save(commit=False)
            bill.company = company
            bill.save()
            formset.instance = bill
            formset.save()
            messages.success(request, f'Bill {bill} created.')
            return redirect('invoicing:bill_detail', pk=bill.pk)
    else:
        form = BillForm(company)
        formset = ItemFormSet()

    return render(request, 'invoicing/bill_form.html', {
        'form': form, 'formset': formset, 'title': 'New Bill',
    })


# ─── Payments ─────────────────────────────────────────────────────────────────

class PaymentListView(CompanyRequiredMixin, ListView):
    model = Payment
    template_name = 'invoicing/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return Payment.objects.filter(company=self.get_company()).select_related('contact')


@login_required
def payment_create(request, invoice_pk=None, bill_pk=None):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')

    invoice = get_object_or_404(Invoice, pk=invoice_pk, company=company) if invoice_pk else None
    bill = get_object_or_404(Bill, pk=bill_pk, company=company) if bill_pk else None

    if request.method == 'POST':
        form = PaymentForm(company, request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.company = company
            payment.invoice = invoice
            payment.bill = bill
            payment.save()
            # Update invoice/bill status
            if invoice:
                if invoice.amount_due <= 0:
                    invoice.status = Invoice.Status.PAID
                else:
                    invoice.status = Invoice.Status.PARTIAL
                invoice.save()
            if bill:
                if bill.amount_due <= 0:
                    bill.status = Bill.Status.PAID
                else:
                    bill.status = Bill.Status.PARTIAL
                bill.save()
            messages.success(request, 'Payment recorded.')
            return redirect('invoicing:payment_list')
    else:
        initial = {}
        if invoice:
            initial = {'contact': invoice.contact, 'amount': invoice.amount_due,
                       'payment_type': Payment.PaymentType.RECEIVED}
        elif bill:
            initial = {'contact': bill.contact, 'amount': bill.amount_due,
                       'payment_type': Payment.PaymentType.MADE}
        form = PaymentForm(company, initial=initial)

    return render(request, 'invoicing/payment_form.html', {
        'form': form, 'invoice': invoice, 'bill': bill,
    })
