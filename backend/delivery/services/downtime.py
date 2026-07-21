"""Calculadora determinística de prejuízo de indisponibilidade de um catálogo de negócio.

Composição travada (decisão do produto): prejuízo total = custo INTERNO + LUCRO CESSANTE +
REGULATÓRIO (usa o lucro cessante, não o faturamento bruto — não superestima; o bruto é
mostrado à parte como referência). Reusa a taxa dia-pessoa global e a moeda/format do core.
"""
from core.utils import get_global_currency, format_currency
from global_settings.models import GlobalSettings

DEFAULT_HOURS = [1, 4, 8, 24, 168]


def _f(v):
    return float(v) if v is not None else 0.0


def compute_catalog_impact(catalog, hours=1, hours_series=None):
    currency = get_global_currency()

    def fmt(v):
        return format_currency(v, currency)

    hourly_cost = catalog.collaborator_hourly_cost
    if hourly_cost is None:
        hourly_cost = GlobalSettings.get_daily_rate() / 8.0  # fallback: dia-pessoa / 8
    hourly_cost = _f(hourly_cost)

    collaborators = catalog.collaborators or 0
    internal_hourly = collaborators * hourly_cost
    revenue_hourly = _f(catalog.hourly_revenue)
    margin = _f(catalog.profit_margin) / 100.0
    lost_profit_hourly = revenue_hourly * margin
    regulatory_hourly = _f(catalog.regulatory_hourly)
    regulatory_fixed = _f(catalog.regulatory_fixed)
    total_hourly = internal_hourly + lost_profit_hourly + regulatory_hourly

    def for_hours(t):
        internal = internal_hourly * t
        lost = lost_profit_hourly * t
        gross = revenue_hourly * t
        reg = regulatory_hourly * t + regulatory_fixed
        total = internal + lost + reg
        return {
            "hours": t,
            "internal": internal, "internal_fmt": fmt(internal),
            "gross_revenue": gross, "gross_revenue_fmt": fmt(gross),
            "lost_profit": lost, "lost_profit_fmt": fmt(lost),
            "regulatory": reg, "regulatory_fmt": fmt(reg),
            "total": total, "total_fmt": fmt(total),
        }

    maintenance = catalog.maintenance_annual_total

    return {
        "currency": currency,
        "collaborators": collaborators,
        "per_collaborator_hourly": hourly_cost,
        "per_collaborator_hourly_fmt": fmt(hourly_cost),
        "profit_margin": _f(catalog.profit_margin),
        "internal_hourly": internal_hourly, "internal_hourly_fmt": fmt(internal_hourly),
        "gross_revenue_hourly": revenue_hourly, "gross_revenue_hourly_fmt": fmt(revenue_hourly),
        "lost_profit_hourly": lost_profit_hourly, "lost_profit_hourly_fmt": fmt(lost_profit_hourly),
        "regulatory_hourly": regulatory_hourly, "regulatory_hourly_fmt": fmt(regulatory_hourly),
        "regulatory_fixed": regulatory_fixed, "regulatory_fixed_fmt": fmt(regulatory_fixed),
        "total_hourly": total_hourly, "total_hourly_fmt": fmt(total_hourly),
        "scenario": for_hours(int(hours) if hours else 1),
        "by_hours": [for_hours(t) for t in (hours_series or DEFAULT_HOURS)],
        "maintenance_annual": maintenance, "maintenance_annual_fmt": fmt(maintenance),
    }
