from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from .models import User, Company


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username', 'email', 'password1', 'password2',
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100 mt-2'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username', 'password',
            Submit('submit', 'Sign In', css_class='btn btn-primary w-100 mt-2'),
        )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'currency', 'fiscal_year_start',
            'address', 'tax_number', 'phone', 'email', 'logo',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('currency', css_class='col-md-6'),
                Column('fiscal_year_start', css_class='col-md-6'),
            ),
            Row(
                Column('phone', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            'tax_number', 'address', 'logo',
            Submit('submit', 'Save Company', css_class='btn btn-primary mt-2'),
        )
