"""
Default Chart of Accounts seeded on new Company creation.
Follows a standard small-business structure with 4-digit account codes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts_app.models import Company


DEFAULT_ACCOUNTS = [
    # code, name, type, parent_code
    # ── Assets ─────────────────────────────────────────────────────────────
    ('1000', 'Assets', 'ASSET', None),
    ('1100', 'Current Assets', 'ASSET', '1000'),
    ('1110', 'Cash and Cash Equivalents', 'ASSET', '1100'),
    ('1120', 'Accounts Receivable', 'ASSET', '1100'),
    ('1130', 'Inventory', 'ASSET', '1100'),
    ('1140', 'Prepaid Expenses', 'ASSET', '1100'),
    ('1200', 'Fixed Assets', 'ASSET', '1000'),
    ('1210', 'Property and Equipment', 'ASSET', '1200'),
    ('1220', 'Accumulated Depreciation', 'ASSET', '1200'),
    # ── Liabilities ────────────────────────────────────────────────────────
    ('2000', 'Liabilities', 'LIABILITY', None),
    ('2100', 'Current Liabilities', 'LIABILITY', '2000'),
    ('2110', 'Accounts Payable', 'LIABILITY', '2100'),
    ('2120', 'Accrued Liabilities', 'LIABILITY', '2100'),
    ('2130', 'Sales Tax Payable', 'LIABILITY', '2100'),
    ('2200', 'Long-term Liabilities', 'LIABILITY', '2000'),
    ('2210', 'Notes Payable', 'LIABILITY', '2200'),
    # ── Equity ─────────────────────────────────────────────────────────────
    ('3000', 'Equity', 'EQUITY', None),
    ('3100', "Owner's Capital", 'EQUITY', '3000'),
    ('3200', "Owner's Drawings", 'EQUITY', '3000'),
    ('3300', 'Retained Earnings', 'EQUITY', '3000'),
    # ── Income ─────────────────────────────────────────────────────────────
    ('4000', 'Income', 'INCOME', None),
    ('4100', 'Sales Revenue', 'INCOME', '4000'),
    ('4200', 'Service Revenue', 'INCOME', '4000'),
    ('4300', 'Other Income', 'INCOME', '4000'),
    # ── Expenses ───────────────────────────────────────────────────────────
    ('5000', 'Expenses', 'EXPENSE', None),
    ('5100', 'Cost of Goods Sold', 'EXPENSE', '5000'),
    ('5200', 'Operating Expenses', 'EXPENSE', '5000'),
    ('5210', 'Salaries and Wages', 'EXPENSE', '5200'),
    ('5220', 'Rent Expense', 'EXPENSE', '5200'),
    ('5230', 'Utilities', 'EXPENSE', '5200'),
    ('5240', 'Office Supplies', 'EXPENSE', '5200'),
    ('5250', 'Marketing and Advertising', 'EXPENSE', '5200'),
    ('5260', 'Insurance', 'EXPENSE', '5200'),
    ('5270', 'Depreciation Expense', 'EXPENSE', '5200'),
    ('5280', 'Bank Charges', 'EXPENSE', '5200'),
    ('5290', 'Professional Fees', 'EXPENSE', '5200'),
    ('5300', 'Travel and Entertainment', 'EXPENSE', '5000'),
    ('5900', 'Income Tax Expense', 'EXPENSE', '5000'),
]


@receiver(post_save, sender=Company)
def seed_chart_of_accounts(sender, instance, created, **kwargs):
    if not created:
        return

    from ledger.models import Account

    code_to_account = {}

    for code, name, account_type, parent_code in DEFAULT_ACCOUNTS:
        parent = code_to_account.get(parent_code) if parent_code else None
        account = Account.objects.create(
            company=instance,
            code=code,
            name=name,
            account_type=account_type,
            parent=parent,
        )
        code_to_account[code] = account
