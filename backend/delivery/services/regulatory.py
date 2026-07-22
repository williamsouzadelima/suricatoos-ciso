"""Resolve as obrigações de notificação regulatória de um incidente a partir do conjunto de
reguladores do cliente (folder → engagement → intake → subsetor → taxonomia) e semeia os
RegulatoryNotification (idempotente). O status `overdue` é calculado em leitura (sem cron)."""
from datetime import timedelta

from django.db import transaction

from delivery.models import Engagement, ClientIntake, RegulatoryNotification
from delivery.taxonomy import suggested_modules
from .reg_obligations import REG_OBLIGATIONS


def resolve_regulator_modules(incident):
    """Módulos regulatórios do cliente dono do incidente. LGPD é o piso transversal."""
    folder = incident.folder
    eng = Engagement.objects.filter(folder=folder).order_by("-created_at").first()
    intake = None
    if eng:
        intake = (
            ClientIntake.objects.filter(engagement=eng).order_by("-created_at").first()
        )
    if intake is None:
        intake = (
            ClientIntake.objects.filter(folder=folder).order_by("-created_at").first()
        )
    subsector = intake.subsector if (intake and intake.subsector) else ""
    mods = list(suggested_modules(subsector)) if subsector else []
    if "lgpd" not in mods:
        mods = ["lgpd"] + mods
    # só módulos que temos obrigação mapeada
    return [m for m in mods if m in REG_OBLIGATIONS]


@transaction.atomic
def seed_regulatory_notifications(incident):
    """Cria (idempotente por incident+module_key+obligation_ref) as notificações regulatórias
    aplicáveis ao cliente do incidente."""
    anchor = incident.reported_at or incident.occurred_at
    modules = resolve_regulator_modules(incident)
    created = 0
    for mod in modules:
        for ob in REG_OBLIGATIONS.get(mod, []):
            dh = ob.get("deadline_hours")
            due = anchor + timedelta(hours=dh) if (anchor and dh) else None
            _obj, was_created = RegulatoryNotification.objects.get_or_create(
                incident=incident,
                module_key=mod,
                obligation_ref=ob["obligation_ref"],
                defaults={
                    "regulator": ob["regulator"],
                    "deadline_hours": dh,
                    "qualitative_note": ob.get("qualitative_note", ""),
                    "channel": ob.get("channel", ""),
                    "triggered_at": anchor,
                    "due_at": due,
                    "template_text": ob.get("template_text", ""),
                },
            )
            if was_created:
                created += 1
    return {"notifications": created, "modules": modules}
