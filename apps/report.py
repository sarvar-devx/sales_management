from django.db.models import Sum, F
from apps.models import Order, Expense, Report

def build_daily_report(date):
    orders = Order.objects.filter(
        status='finished',
        finished_at__date=date
    )

    selling = orders.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    arrival_cost = orders.aggregate(
        total=Sum(F('product__arrival_price') * F('quantity'))
    )['total'] or 0

    benefit = selling - arrival_cost

    expenses = Expense.objects.filter(
        date__date=date
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    Report.objects.update_or_create(
        date=date,
        defaults={
            'selling': selling,
            'benefit': benefit,
            'expenses': expenses
        }
    )
