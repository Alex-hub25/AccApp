from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm, CompanyForm
from .models import Company


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Create your first company to get started.')
            return redirect('accounts:company_create')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'accounts/company_list.html'
    context_object_name = 'companies'

    def get_queryset(self):
        return Company.objects.filter(owner=self.request.user)


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'accounts/company_form.html'
    success_url = reverse_lazy('accounts:company_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # Set as active company if user has none
        profile = self.request.user.profile
        if not profile.active_company:
            profile.active_company = self.object
            profile.save()
        messages.success(self.request, f'Company "{self.object.name}" created.')
        return response


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'accounts/company_form.html'
    success_url = reverse_lazy('accounts:company_list')

    def get_queryset(self):
        return Company.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Company updated.')
        return super().form_valid(form)


@login_required
def switch_company(request, pk):
    company = get_object_or_404(Company, pk=pk, owner=request.user)
    request.user.profile.active_company = company
    request.user.profile.save()
    messages.success(request, f'Switched to {company.name}.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))

