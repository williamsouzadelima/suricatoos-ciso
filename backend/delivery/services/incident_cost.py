"""P&L determinístico de um incidente. Reusa compute_catalog_impact (impacto de negócio via
downtime dos catálogos ligados aos ativos do incidente) + a taxa dia-pessoa global para o
esforço de resposta. Nunca fabrica número — tudo deriva de inputs reais.

Composição: total = esforço de resposta + impacto de negócio + fornecedores externos + multas.
(Apontamento de horas REAL por incidente fica p/ 2ª onda; hoje usa as horas estimadas.)"""
from core.utils import get_global_currency, format_currency
from global_settings.models import GlobalSettings

from delivery.models import IncidentResponseTask, IncidentTimeEntry, BusinessCatalog
from .downtime import compute_catalog_impact


def _f(v):
    return float(v) if v is not None else 0.0


def _incident_downtime_hours(incident, cost):
    if cost and cost.downtime_hours is not None:
        return _f(cost.downtime_hours)
    if incident.resolved_at and incident.reported_at:
        delta = incident.resolved_at - incident.reported_at
        return max(delta.total_seconds() / 3600.0, 0.0)
    return 0.0


def compute_incident_cost(incident, hours_series=None):
    cost = getattr(incident, "ir_cost", None)
    currency = (cost.currency if (cost and cost.currency) else "") or get_global_currency()

    def fmt(v):
        return format_currency(v, currency)

    # 1) esforço de resposta = horas × (diária global / 8). Usa as horas REALMENTE
    #    apontadas (IncidentTimeEntry) se houver; senão, cai para as horas estimadas.
    hourly_rate = float(GlobalSettings.get_daily_rate()) / 8.0
    est_hours = 0.0
    for t in IncidentResponseTask.objects.filter(incident=incident):
        est_hours += _f(t.estimated_hours)
    logged_hours = 0.0
    for te in IncidentTimeEntry.objects.filter(incident=incident):
        logged_hours += _f(te.hours)
    if logged_hours > 0:
        effort_hours = logged_hours
        effort_basis = "logged"
    else:
        effort_hours = est_hours
        effort_basis = "estimated"
    response_effort = effort_hours * hourly_rate

    # 2) impacto de negócio = downtime aplicado aos catálogos ligados aos ativos do incidente
    #    (mapeamento preciso via CatalogDependency.asset). Nota: se catálogos usarem moedas
    #    distintas, o total assume a moeda do incidente; cada by_asset mostra a sua própria.
    downtime_hours = _incident_downtime_hours(incident, cost)
    by_asset = []
    business_impact = 0.0
    asset_ids = list(incident.assets.values_list("id", flat=True))
    if asset_ids and downtime_hours > 0:
        catalogs = BusinessCatalog.objects.filter(
            dependencies__asset__in=asset_ids
        ).distinct()
        for cat in catalogs:
            imp = compute_catalog_impact(cat, hours=downtime_hours)
            total = imp["scenario"]["total"]
            business_impact += total
            by_asset.append(
                {
                    "catalog": cat.name,
                    "total": total,
                    "total_fmt": format_currency(total, imp["currency"]),
                }
            )

    # 3) fornecedores externos + multas (linhas manuais do IncidentCost)
    if cost:
        external_vendor = (
            _f(cost.vendor_forensics) + _f(cost.vendor_legal) + _f(cost.other_external)
        )
        regulatory_fines = _f(cost.regulatory_fines)
    else:
        external_vendor = 0.0
        regulatory_fines = 0.0

    total = response_effort + business_impact + external_vendor + regulatory_fines

    return {
        "currency": currency,
        "hourly_rate": hourly_rate,
        "hourly_rate_fmt": fmt(hourly_rate),
        "estimated_hours": est_hours,
        "logged_hours": logged_hours,
        "effort_hours": effort_hours,
        "effort_basis": effort_basis,
        "downtime_hours": downtime_hours,
        "response_effort": response_effort,
        "response_effort_fmt": fmt(response_effort),
        "business_impact": business_impact,
        "business_impact_fmt": fmt(business_impact),
        "external_vendor": external_vendor,
        "external_vendor_fmt": fmt(external_vendor),
        "regulatory_fines": regulatory_fines,
        "regulatory_fines_fmt": fmt(regulatory_fines),
        "total": total,
        "total_fmt": fmt(total),
        "by_asset": by_asset,
    }
