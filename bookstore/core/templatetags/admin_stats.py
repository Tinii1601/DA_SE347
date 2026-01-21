import json
from datetime import timedelta
from decimal import Decimal

from django import template
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek, Coalesce
from django.utils import timezone
from django.utils.safestring import mark_safe

from payment.models import Payment

register = template.Library()


def _serialize_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def _build_series(labels, value_map):
    data = [value_map.get(label, 0) for label in labels]
    return data


@register.simple_tag
def revenue_chart_data():
    now = timezone.localtime(timezone.now())

    # Daily: last 7 days (including today)
    daily_start = (now - timedelta(days=6)).date()
    daily_labels = [(daily_start + timedelta(days=i)).strftime("%d/%m") for i in range(7)]
    daily_values = {}
    daily_qs = (
        Payment.objects.filter(status="completed")
        .annotate(ts=Coalesce("paid_at", "created_at"))
        .filter(ts__date__gte=daily_start)
        .annotate(day=TruncDay("ts"))
        .values("day")
        .annotate(total=Sum("amount"))
        .order_by("day")
    )
    for row in daily_qs:
        label = timezone.localtime(row["day"]).strftime("%d/%m")
        daily_values[label] = _serialize_decimal(row["total"])

    # Weekly: last 8 weeks
    week_start = (now - timedelta(weeks=7)).date()
    weekly_labels = []
    weekly_values = {}
    for i in range(8):
        start = week_start + timedelta(weeks=i)
        weekly_labels.append(start.strftime("Tuần %W"))
    weekly_qs = (
        Payment.objects.filter(status="completed")
        .annotate(ts=Coalesce("paid_at", "created_at"))
        .filter(ts__date__gte=week_start)
        .annotate(week=TruncWeek("ts"))
        .values("week")
        .annotate(total=Sum("amount"))
        .order_by("week")
    )
    for row in weekly_qs:
        label = timezone.localtime(row["week"]).strftime("Tuần %W")
        weekly_values[label] = _serialize_decimal(row["total"])

    # Monthly: last 6 months
    first_month = (now.replace(day=1) - timedelta(days=30 * 5)).date()
    monthly_labels = []
    monthly_values = {}
    current = first_month
    for _ in range(6):
        monthly_labels.append(current.strftime("%m/%Y"))
        # move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    monthly_qs = (
        Payment.objects.filter(status="completed")
        .annotate(ts=Coalesce("paid_at", "created_at"))
        .filter(ts__date__gte=first_month)
        .annotate(month=TruncMonth("ts"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    for row in monthly_qs:
        label = timezone.localtime(row["month"]).strftime("%m/%Y")
        monthly_values[label] = _serialize_decimal(row["total"])

    payload = {
        "daily": {"labels": daily_labels, "data": _build_series(daily_labels, daily_values)},
        "weekly": {"labels": weekly_labels, "data": _build_series(weekly_labels, weekly_values)},
        "monthly": {"labels": monthly_labels, "data": _build_series(monthly_labels, monthly_values)},
    }
    return mark_safe(json.dumps(payload, ensure_ascii=False))
