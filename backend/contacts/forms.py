from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['contact_type', 'name', 'email', 'phone', 'address', 'tax_number', 'notes', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('contact_type', css_class='col-md-6'), Column('name', css_class='col-md-6')),
            Row(Column('email', css_class='col-md-6'), Column('phone', css_class='col-md-6')),
            'tax_number', 'address', 'notes', 'is_active',
            Submit('submit', 'Save Contact', css_class='btn btn-primary mt-2'),
        )
