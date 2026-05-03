from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q

from ledger.models import Account, JournalEntryLine, AccountType


def _get_company(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return request.user.profile.active_company
    return None


def _account_balance(account, date_from=None, date_to=None):
    """Calculate account balance for a date range (or all time if not specified)."""
    qs = JournalEntryLine.objects.filter(account=account, entry__is_posted=True)
    if date_from:
        qs = qs.filter(entry__date__gte=date_from)
    if date_to:
        qs = qs.filter(entry__date__lte=date_to)
    debit = qs.aggregate(t=Sum('debit'))['t'] or Decimal('0')
    credit = qs.aggregate(t=Sum('credit'))['t'] or Decimal('0')
    if account.account_type in ('ASSET', 'EXPENSE'):
        return debit - credit
    return credit - debit


@login_required
def trial_balance(request):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')

    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or date.today().isoformat()

    accounts = Account.objects.filter(company=company, is_active=True).order_by('code')
    rows = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')

    for acc in accounts:
        bal = _account_balance(acc, date_from, date_to)
        if bal == 0:
            continue
        if acc.account_type in ('ASSET', 'EXPENSE'):
            debit_col = bal if bal > 0 else Decimal('0')
            credit_col = abs(bal) if bal < 0 else Decimal('0')
        else:
            credit_col = bal if bal > 0 else Decimal('0')
            debit_col = abs(bal) if bal < 0 else Decimal('0')
        total_debit += debit_col
        total_credit += credit_col
        rows.append({'account': acc, 'debit': debit_col, 'credit': credit_col})

    ctx = {
        'rows': rows,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'balanced': total_debit == total_credit,
        'date_from': date_from or '',
        'date_to': date_to,
    }
    if request.htmx:
        return render(request, 'reports/partials/trial_balance_table.html', ctx)
    return render(request, 'reports/trial_balance.html', ctx)


@login_required
def profit_and_loss(request):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')

    date_from = request.GET.get('date_from') or date(date.today().year, 1, 1).isoformat()
    date_to = request.GET.get('date_to') or date.today().isoformat()

    income_accounts = Account.objects.filter(
        company=company, account_type=AccountType.INCOME, is_active=True
    ).order_by('code')
    expense_accounts = Account.objects.filter(
        company=company, account_type=AccountType.EXPENSE, is_active=True
    ).order_by('code')

    income_rows = []
    total_income = Decimal('0')
    for acc in income_accounts:
        bal = _account_balance(acc, date_from, date_to)
        if bal:
            income_rows.append({'account': acc, 'amount': bal})
            total_income += bal

    expense_rows = []
    total_expenses = Decimal('0')
    for acc in expense_accounts:
        bal = _account_balance(acc, date_from, date_to)
        if bal:
            expense_rows.append({'account': acc, 'amount': bal})
            total_expenses += bal

    net_income = total_income - total_expenses

    ctx = {
        'income_rows': income_rows,
        'expense_rows': expense_rows,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'date_from': date_from,
        'date_to': date_to,
    }
    if request.htmx:
        return render(request, 'reports/partials/pl_table.html', ctx)
    return render(request, 'reports/profit_and_loss.html', ctx)


@login_required
def balance_sheet(request):
    company = _get_company(request)
    if not company:
        return redirect('accounts:company_list')

    as_of = request.GET.get('as_of') or date.today().isoformat()

    asset_accounts = Account.objects.filter(
        company=company, account_type=AccountType.ASSET, is_active=True
    ).order_by('code')
    liability_accounts = Account.objects.filter(
        company=company, account_type=AccountType.LIABILITY, is_active=True
    ).order_by('code')
    equity_accounts = Account.objects.filter(
        company=company, account_type=AccountType.EQUITY, is_active=True
    ).order_by('code')

    # Balance sheet uses cumulative balances from inception to as_of date
    asset_rows, total_assets = [], Decimal('0')
    for acc in asset_accounts:
        bal = _account_balance(acc, date_to=as_of)
        if bal:
            asset_rows.append({'account': acc, 'amount': bal})
            total_assets += bal

    liability_rows, total_liabilities = [], Decimal('0')
    for acc in liability_accounts:
        bal = _account_balance(acc, date_to=as_of)
        if bal:
            liability_rows.append({'account': acc, 'amount': bal})
            total_liabilities += bal

    equity_rows, total_equity = [], Decimal('0')
    for acc in equity_accounts:
        bal = _account_balance(acc, date_to=as_of)
        if bal:
            equity_rows.append({'account': acc, 'amount': bal})
            total_equity += bal

    # Add current period retained earnings (net income to date)
    income_accounts = Account.objects.filter(company=company, account_type=AccountType.INCOME)
    expense_accounts = Account.objects.filter(company=company, account_type=AccountType.EXPENSE)
    current_income = sum(_account_balance(a, date_to=as_of) for a in income_accounts)
    current_expenses = sum(_account_balance(a, date_to=as_of) for a in expense_accounts)
    current_net = current_income - current_expenses
    total_equity += current_net

    ctx = {
        'asset_rows': asset_rows,
        'liability_rows': liability_rows,
        'equity_rows': equity_rows,
        'current_net_income': current_net,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'total_liabilities_equity': total_liabilities + total_equity,
        'balanced': total_assets == total_liabilities + total_equity,
        'as_of': as_of,
    }
    if request.htmx:
        return render(request, 'reports/partials/balance_sheet_table.html', ctx)
    return render(request, 'reports/balance_sheet.html', ctx)
