from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import Account, JournalEntry, JournalEntryLine


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'account_type', 'parent', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Account.objects.filter(company=company)
        self.fields['parent'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('code', css_class='col-md-4'), Column('name', css_class='col-md-8')),
            Row(Column('account_type', css_class='col-md-6'), Column('parent', css_class='col-md-6')),
            'description', 'is_active',
            Submit('submit', 'Save Account', css_class='btn btn-primary mt-2'),
        )


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['date', 'reference', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class JournalEntryLineForm(forms.ModelForm):
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'description', 'debit', 'credit']

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(company=company, is_active=True)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True


def get_line_formset(company, extra=2):
    """Return an inline formset factory with company-scoped account queryset."""
    FormSet = inlineformset_factory(
        JournalEntry, JournalEntryLine,
        form=JournalEntryLineForm,
        extra=extra,
        can_delete=True,
    )

    class BoundFormSet(FormSet):
        def _construct_form(self, i, **kwargs):
            form = super()._construct_form(i, **kwargs)
            form.fields['account'].queryset = Account.objects.filter(
                company=company, is_active=True
            )
            return form

    return BoundFormSet
