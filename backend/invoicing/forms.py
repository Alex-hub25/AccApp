from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Invoice, InvoiceItem, Bill, BillItem, Payment
from contacts.models import Contact
from taxes.models import TaxRate
from ledger.models import Account


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['contact', 'invoice_number', 'date', 'due_date', 'tax_rate', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(
            company=company, contact_type__in=['CUSTOMER', 'BOTH'], is_active=True
        )
        self.fields['tax_rate'].queryset = TaxRate.objects.filter(company=company, is_active=True)
        self.fields['tax_rate'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price', 'account']

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(
            company=company, account_type='INCOME', is_active=True
        )
        self.fields['account'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True


def get_invoice_item_formset(company, extra=3):
    FormSet = inlineformset_factory(
        Invoice, InvoiceItem, form=InvoiceItemForm,
        extra=extra, can_delete=True,
    )

    class BoundFormSet(FormSet):
        def _construct_form(self, i, **kwargs):
            form = super()._construct_form(i, **kwargs)
            form.fields['account'].queryset = Account.objects.filter(
                company=company, account_type='INCOME', is_active=True
            )
            return form

    return BoundFormSet


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['contact', 'bill_number', 'date', 'due_date', 'tax_rate', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(
            company=company, contact_type__in=['VENDOR', 'BOTH'], is_active=True
        )
        self.fields['tax_rate'].queryset = TaxRate.objects.filter(company=company, is_active=True)
        self.fields['tax_rate'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False


class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['description', 'quantity', 'unit_price', 'account']

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(
            company=company, account_type='EXPENSE', is_active=True
        )
        self.fields['account'].required = False


def get_bill_item_formset(company, extra=3):
    FormSet = inlineformset_factory(
        Bill, BillItem, form=BillItemForm,
        extra=extra, can_delete=True,
    )

    class BoundFormSet(FormSet):
        def _construct_form(self, i, **kwargs):
            form = super()._construct_form(i, **kwargs)
            form.fields['account'].queryset = Account.objects.filter(
                company=company, account_type='EXPENSE', is_active=True
            )
            return form

    return BoundFormSet


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type', 'contact', 'amount', 'date', 'reference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.filter(company=company, is_active=True)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('payment_type', css_class='col-md-6'), Column('contact', css_class='col-md-6')),
            Row(Column('amount', css_class='col-md-6'), Column('date', css_class='col-md-6')),
            'reference', 'notes',
            Submit('submit', 'Record Payment', css_class='btn btn-primary mt-2'),
        )
