from django.db import models
from core.models import TimeStampedModel
from accounts_app.models import Company


class Contact(TimeStampedModel):
    class ContactType(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        VENDOR = 'VENDOR', 'Vendor'
        BOTH = 'BOTH', 'Customer & Vendor'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=10, choices=ContactType.choices, default=ContactType.CUSTOMER)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=50, blank=True, verbose_name='Tax/VAT Number')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ['company', 'name']

    def __str__(self):
        return self.name

    @property
    def is_customer(self):
        return self.contact_type in (self.ContactType.CUSTOMER, self.ContactType.BOTH)

    @property
    def is_vendor(self):
        return self.contact_type in (self.ContactType.VENDOR, self.ContactType.BOTH)
