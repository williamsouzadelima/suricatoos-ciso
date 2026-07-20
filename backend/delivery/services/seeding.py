"""Seed de plano de engajamento vCISO — materializa o playbook curado como AppliedControls
reais no folder do cliente (caem no Kanban existente) + a camada PlanTask (fase/horas).
Idempotente por PlanTask.template_key.
"""
import pathlib
from datetime import timedelta

import yaml
from django.db import transaction

from core.models import AppliedControl
from delivery.models import EngagementPhase, PlanTask

PLAYBOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / "playbooks"

# template key -> arquivo do núcleo
TEMPLATE_FILES = {
    "vciso-100d": "vciso_100d_core.yaml",
}


def _load_yaml(name):
    return yaml.safe_load((PLAYBOOKS_DIR / name).read_text(encoding="utf-8"))


def load_playbook(template="vciso-100d", modules=None):
    """Carrega o núcleo e mescla as tarefas dos módulos regulatórios (por phase_key)."""
    core_file = TEMPLATE_FILES.get(template)
    if not core_file:
        raise ValueError(f"template desconhecido: {template}")
    core = _load_yaml(core_file)
    phases = {p["key"]: p for p in core["phases"]}
    for p in phases.values():
        p.setdefault("tasks", [])
    for mod in modules or []:
        m = _load_yaml(f"mod_{mod}.yaml")
        for t in m.get("tasks", []):
            pk = t.get("phase_key")
            if pk in phases:
                phases[pk]["tasks"].append(t)
    return core


@transaction.atomic
def seed_engagement_plan(engagement, template="vciso-100d", modules=None):
    """Semeia (idempotente) o plano no engajamento. Requer engagement.day_zero."""
    day_zero = engagement.day_zero
    if day_zero is None:
        raise ValueError("engagement.day_zero precisa estar setado antes do seed.")
    playbook = load_playbook(template, modules)
    created_ac = 0
    created_pt = 0
    for phase_data in playbook["phases"]:
        phase, _ = EngagementPhase.objects.get_or_create(
            engagement=engagement,
            order=phase_data["order"],
            defaults={
                "name": phase_data["name"],
                "day_start": phase_data["day_start"],
                "day_end": phase_data["day_end"],
                "objective": phase_data.get("objective", ""),
            },
        )
        for i, task in enumerate(phase_data.get("tasks", [])):
            tkey = f"{template}:{task['key']}"
            if PlanTask.objects.filter(
                engagement=engagement, template_key=tkey
            ).exists():
                continue
            offset = int(task.get("offset_start_days", 0))
            dur = int(task.get("duration_days", 7))
            ac = AppliedControl.objects.create(
                folder=engagement.folder,
                name=task["name"],
                description=task.get("description", ""),
                priority=task.get("priority"),
                effort=task.get("effort"),
                status="to_do",
                start_date=day_zero + timedelta(days=offset),
                eta=day_zero + timedelta(days=offset + dur),
            )
            created_ac += 1
            PlanTask.objects.create(
                engagement=engagement,
                phase=phase,
                applied_control=ac,
                estimated_hours=task.get("estimated_hours"),
                order=i,
                template_key=tkey,
            )
            created_pt += 1
    return {"applied_controls": created_ac, "plan_tasks": created_pt}
