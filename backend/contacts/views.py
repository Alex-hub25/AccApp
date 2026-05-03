from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import HttpResponse

from core.mixins import CompanyRequiredMixin
from .models import Contact
from .forms import ContactForm


class ContactListView(CompanyRequiredMixin, ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        qs = Contact.objects.filter(company=self.get_company())
        q = self.request.GET.get('q', '').strip()
        contact_type = self.request.GET.get('type', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        if contact_type:
            qs = qs.filter(contact_type=contact_type)
        return qs

    def get_template_names(self):
        if self.request.htmx:
            return ['contacts/partials/contact_table.html']
        return [self.template_name]


class ContactDetailView(CompanyRequiredMixin, DetailView):
    model = Contact
    template_name = 'contacts/contact_detail.html'

    def get_queryset(self):
        return Contact.objects.filter(company=self.get_company())


class ContactCreateView(CompanyRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contacts:list')

    def form_valid(self, form):
        form.instance.company = self.get_company()
        messages.success(self.request, 'Contact created.')
        return super().form_valid(form)


class ContactUpdateView(CompanyRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contacts:list')

    def get_queryset(self):
        return Contact.objects.filter(company=self.get_company())

    def form_valid(self, form):
        messages.success(self.request, 'Contact updated.')
        return super().form_valid(form)
