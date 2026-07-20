"""Derivação da matriz de Eisenhower (2x2) a partir de um PlanTask.

Importância = importance_override, senão priority in {P1,P2} (AppliedControl.priority 1/2).
Urgência   = urgency_override, senão priority==P1 OU eta dentro do horizonte (dias).
Quadrantes: U×I=do (fazer) · ¬U×I=schedule (agendar) · U×¬I=delegate (delegar) · ¬U×¬I=eliminate (eliminar).
"""
from django.utils import timezone

QUADRANTS = {
    (1, 1): "do",
    (0, 1): "schedule",
    (1, 0): "delegate",
    (0, 0): "eliminate",
}

DEFAULT_HORIZON_DAYS = 21


def derive_eisenhower(plan_task, today=None, horizon_days=DEFAULT_HORIZON_DAYS):
    today = today or timezone.now().date()
    ac = getattr(plan_task, "applied_control", None)
    priority = getattr(ac, "priority", None) if ac else None
    eta = getattr(ac, "eta", None) if ac else None

    importance = plan_task.importance_override
    if importance is None:
        importance = 1 if priority in (1, 2) else 0

    urgency = plan_task.urgency_override
    if urgency is None:
        urgency = 0
        if priority == 1:
            urgency = 1
        elif eta is not None and (eta - today).days <= horizon_days:
            urgency = 1

    importance = 1 if importance else 0
    urgency = 1 if urgency else 0
    return {
        "urgency": urgency,
        "importance": importance,
        "quadrant": QUADRANTS[(urgency, importance)],
        "priority": priority,
        "eta": eta,
        "horizon_days": horizon_days,
    }
