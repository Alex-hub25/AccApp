from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from core.models import TimeStampedModel
from accounts_app.models import Company


class AccountType(models.TextChoices):
    ASSET = 'ASSET', 'Asset'
    LIABILITY = 'LIABILITY', 'Liability'
    EQUITY = 'EQUITY', 'Equity'
    INCOME = 'INCOME', 'Income'
    EXPENSE = 'EXPENSE', 'Expense'


# Normal balance: debit increases Assets & Expenses; credit increases Liabilities, Equity, Income
DEBIT_NORMAL = {AccountType.ASSET, AccountType.EXPENSE}
CREDIT_NORMAL = {AccountType.LIABILITY, AccountType.EQUITY, AccountType.INCOME}


class Account(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        unique_together = ['company', 'code']

    def __str__(self):
        return f'{self.code} – {self.name}'

    @property
    def balance(self):
        """Net balance calculated from posted journal entry lines."""
        lines = JournalEntryLine.objects.filter(
            account=self, entry__is_posted=True
        )
        debit_total = lines.aggregate(t=Sum('debit'))['t'] or 0
        credit_total = lines.aggregate(t=Sum('credit'))['t'] or 0
        if self.account_type in DEBIT_NORMAL:
            return debit_total - credit_total
        return credit_total - debit_total


class JournalEntry(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField()
    reference = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    is_posted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'journal entries'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'JE-{self.pk} {self.date} {self.description[:40]}'

    def clean(self):
        lines = self.lines.all()
        if lines.exists():
            total_debit = lines.aggregate(t=Sum('debit'))['t'] or 0
            total_credit = lines.aggregate(t=Sum('credit'))['t'] or 0
            if total_debit != total_credit:
                raise ValidationError('Journal entry is not balanced: debits must equal credits.')

    @property
    def total_debit(self):
        return self.lines.aggregate(t=Sum('debit'))['t'] or 0

    @property
    def total_credit(self):
        return self.lines.aggregate(t=Sum('credit'))['t'] or 0


class JournalEntryLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='entry_lines')
    description = models.CharField(max_length=200, blank=True)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['pk']

    def clean(self):
        if self.debit < 0 or self.credit < 0:
            raise ValidationError('Debit and credit amounts cannot be negative.')
        if self.debit > 0 and self.credit > 0:
            raise ValidationError('A line cannot have both a debit and a credit amount.')

    def __str__(self):
        return f'{self.account} Dr:{self.debit} Cr:{self.credit}'
