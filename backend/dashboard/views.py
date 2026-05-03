from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q

from invoicing.models import Invoice, Bill, Payment
from expenses.models import Expense
from ledger.models import JournalEntryLine, Account, AccountType


@login_required
def index(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.active_company:
        return redirect('accounts:company_list')

    company = request.user.profile.active_company
    today = date.today()
    month_start = date(today.year, today.month, 1)

    # ── Summary cards ─────────────────────────────────────────────────────────
    total_receivable = Invoice.objects.filter(
        company=company, status__in=['SENT', 'PARTIAL', 'OVERDUE']
    ).aggregate(
        t=Sum('items__quantity') * Sum('items__unit_price')
    )['t'] or Decimal('0')

    # Simplified: sum amount_due via Python for accuracy
    open_invoices = Invoice.objects.filter(
        company=company, status__in=['SENT', 'PARTIAL', 'OVERDUE']
    ).prefetch_related('items', 'payments')
    total_receivable = sum(inv.amount_due for inv in open_invoices)

    open_bills = Bill.objects.filter(
        company=company, status__in=['RECEIVED', 'PARTIAL', 'OVERDUE']
    ).prefetch_related('items', 'payments')
    total_payable = sum(bill.amount_due for bill in open_bills)

    # Cash: balance of account code 1110 (Cash and Cash Equivalents)
    cash_account = Account.objects.filter(company=company, code='1110').first()
    cash_balance = cash_account.balance if cash_account else Decimal('0')

    # Income vs Expenses this month
    income_this_month = Decimal('0')
    for acc in Account.objects.filter(company=company, account_type=AccountType.INCOME):
        lines = JournalEntryLine.objects.filter(
            account=acc, entry__is_posted=True,
            entry__date__gte=month_start, entry__date__lte=today,
        )
        c = lines.aggregate(t=Sum('credit'))['t'] or Decimal('0')
        d = lines.aggregate(t=Sum('debit'))['t'] or Decimal('0')
        income_this_month += c - d

    expenses_this_month = Decimal('0')
    for acc in Account.objects.filter(company=company, account_type=AccountType.EXPENSE):
        lines = JournalEntryLine.objects.filter(
            account=acc, entry__is_posted=True,
            entry__date__gte=month_start, entry__date__lte=today,
        )
        d = lines.aggregate(t=Sum('debit'))['t'] or Decimal('0')
        c = lines.aggregate(t=Sum('credit'))['t'] or Decimal('0')
        expenses_this_month += d - c

    # ── Recent activity ───────────────────────────────────────────────────────
    recent_invoices = Invoice.objects.filter(company=company).order_by('-date')[:5]
    recent_expenses = Expense.objects.filter(company=company).order_by('-date')[:5]

    # ── Monthly chart data (last 6 months) ────────────────────────────────────
    chart_labels = []
    chart_income = []
    chart_expenses = []
    for i in range(5, -1, -1):
        import calendar
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        _, last_day = calendar.monthrange(year, month)
        m_start = date(year, month, 1)
        m_end = date(year, month, last_day)
        chart_labels.append(m_start.strftime('%b %Y'))

        m_income = Decimal('0')
        for acc in Account.objects.filter(company=company, account_type=AccountType.INCOME):
            lines = JournalEntryLine.objects.filter(
                account=acc, entry__is_posted=True,
                entry__date__gte=m_start, entry__date__lte=m_end,
            )
            c = lines.aggregate(t=Sum('credit'))['t'] or Decimal('0')
            d = lines.aggregate(t=Sum('debit'))['t'] or Decimal('0')
            m_income += c - d
        chart_income.append(float(m_income))

        m_expense = Decimal('0')
        for acc in Account.objects.filter(company=company, account_type=AccountType.EXPENSE):
            lines = JournalEntryLine.objects.filter(
                account=acc, entry__is_posted=True,
                entry__date__gte=m_start, entry__date__lte=m_end,
            )
            d = lines.aggregate(t=Sum('debit'))['t'] or Decimal('0')
            c = lines.aggregate(t=Sum('credit'))['t'] or Decimal('0')
            m_expense += d - c
        chart_expenses.append(float(m_expense))

    return render(request, 'dashboard/index.html', {
        'total_receivable': total_receivable,
        'total_payable': total_payable,
        'cash_balance': cash_balance,
        'net_income_this_month': income_this_month - expenses_this_month,
        'recent_invoices': recent_invoices,
        'recent_expenses': recent_expenses,
        'chart_labels': chart_labels,
        'chart_income': chart_income,
        'chart_expenses': chart_expenses,
    })
