from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import TaxRate


class TaxRateForm(forms.ModelForm):
    class Meta:
        model = TaxRate
        fields = ['name', 'rate', 'is_active']
        help_texts = {'rate': 'Enter as decimal e.g. 0.10 for 10%'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(Column('rate', css_class='col-md-6'), Column('is_active', css_class='col-md-6')),
            Submit('submit', 'Save', css_class='btn btn-primary mt-2'),
        )
