from django.db import models
from core.models import TimeStampedModel
from accounts_app.models import Company
from contacts.models import Contact
from taxes.models import TaxRate


class Expense(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    account = models.ForeignKey(
        'ledger.Account', on_delete=models.PROTECT, related_name='expenses'
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses'
    )
    tax_rate = models.ForeignKey(
        TaxRate, on_delete=models.SET_NULL, null=True, blank=True
    )
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.date} {self.description} {self.amount}'

    @property
    def tax_amount(self):
        if self.tax_rate:
            return self.amount * self.tax_rate.rate
        return 0

    @property
    def total_with_tax(self):
        return self.amount + self.tax_amount
