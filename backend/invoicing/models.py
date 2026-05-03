from django.db import models
from django.db.models import Sum
from core.models import TimeStampedModel
from accounts_app.models import Company
from contacts.models import Contact
from taxes.models import TaxRate


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'
        VOID = 'VOID', 'Void'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoices')
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50)
    date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['company', 'invoice_number']

    def __str__(self):
        return f'INV-{self.invoice_number}'

    @property
    def subtotal(self):
        return self.items.aggregate(
            t=Sum(models.F('quantity') * models.F('unit_price'))
        )['t'] or 0

    @property
    def tax_amount(self):
        if self.tax_rate:
            return self.subtotal * self.tax_rate.rate
        return 0

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def amount_paid(self):
        return self.payments.filter(
            payment_type=Payment.PaymentType.RECEIVED
        ).aggregate(t=Sum('amount'))['t'] or 0

    @property
    def amount_due(self):
        return self.total - self.amount_paid


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    account = models.ForeignKey(
        'ledger.Account', on_delete=models.PROTECT, related_name='invoice_items',
        null=True, blank=True
    )

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Bill(TimeStampedModel):
    """Accounts Payable — vendor bill."""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        RECEIVED = 'RECEIVED', 'Received'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'
        VOID = 'VOID', 'Void'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bills')
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='bills')
    bill_number = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'BILL-{self.pk}'

    @property
    def subtotal(self):
        return self.items.aggregate(
            t=Sum(models.F('quantity') * models.F('unit_price'))
        )['t'] or 0

    @property
    def tax_amount(self):
        if self.tax_rate:
            return self.subtotal * self.tax_rate.rate
        return 0

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def amount_paid(self):
        return self.payments.filter(
            payment_type=Payment.PaymentType.MADE
        ).aggregate(t=Sum('amount'))['t'] or 0

    @property
    def amount_due(self):
        return self.total - self.amount_paid


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    account = models.ForeignKey(
        'ledger.Account', on_delete=models.PROTECT, related_name='bill_items',
        null=True, blank=True
    )

    class Meta:
        ordering = ['pk']

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Payment(TimeStampedModel):
    class PaymentType(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Payment Received'
        MADE = 'MADE', 'Payment Made'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    bill = models.ForeignKey(
        Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    journal_entry = models.ForeignKey(
        'ledger.JournalEntry', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'PMT-{self.pk} {self.payment_type} {self.amount}'
