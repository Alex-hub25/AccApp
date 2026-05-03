from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class CompanyRequiredMixin(LoginRequiredMixin):
    """Mixin that ensures a user has an active company selected."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, 'profile') or not request.user.profile.active_company:
            messages.warning(request, 'Please create or select a company first.')
            return redirect('accounts:company_list')
        return super().dispatch(request, *args, **kwargs)

    def get_company(self):
        return self.request.user.profile.active_company
