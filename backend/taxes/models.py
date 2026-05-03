from django.db import models
from core.models import TimeStampedModel
from accounts_app.models import Company


class TaxRate(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_rates')
    name = models.CharField(max_length=100, help_text='e.g. GST 10%, Sales Tax 8%')
    rate = models.DecimalField(max_digits=6, decimal_places=4, help_text='e.g. 0.1000 for 10%')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ['company', 'name']

    def __str__(self):
        return f'{self.name} ({self.rate * 100:.2f}%)'

    @property
    def rate_percent(self):
        return self.rate * 100
