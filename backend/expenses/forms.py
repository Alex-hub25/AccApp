from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Expense
from contacts.models import Contact
from taxes.models import TaxRate
from ledger.models import Account


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'description', 'amount', 'account', 'contact', 'tax_rate', 'receipt', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(
            company=company, account_type='EXPENSE', is_active=True
        )
        self.fields['contact'].queryset = Contact.objects.filter(
            company=company, contact_type__in=['VENDOR', 'BOTH'], is_active=True
        )
        self.fields['contact'].required = False
        self.fields['tax_rate'].queryset = TaxRate.objects.filter(company=company, is_active=True)
        self.fields['tax_rate'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('date', css_class='col-md-6'), Column('amount', css_class='col-md-6')),
            'description',
            Row(Column('account', css_class='col-md-6'), Column('tax_rate', css_class='col-md-6')),
            Row(Column('contact', css_class='col-md-6'), Column('receipt', css_class='col-md-6')),
            'notes',
            Submit('submit', 'Save Expense', css_class='btn btn-primary mt-2'),
        )
