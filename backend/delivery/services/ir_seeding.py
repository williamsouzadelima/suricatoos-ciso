"""Semeador do runbook de resposta a incidentes — espelha services/seeding.py, mas materializa
cada atividade como core.AppliedControl (adicionada a incident.applied_controls, então aparece
no Kanban/Gantt) + uma ponte IncidentResponseTask idempotente por template_key."""
import pathlib

import yaml
from datetime import timedelta

from django.db import transaction
from django.utils.timezone import now

from core.models import AppliedControl
from delivery.models import (
    IncidentResponsePlan,
    IncidentPhase,
    IncidentResponseTask,
)

PLAYBOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / "playbooks"

IR_TEMPLATE_FILES = {
    "nist-800-61": "ir_nist_800_61.yaml",
    "iso-27035": "ir_iso_27035.yaml",
}


def _load_yaml(name):
    return yaml.safe_load((PLAYBOOKS_DIR / name).read_text(encoding="utf-8"))


def load_ir_playbook(standard="nist-800-61", modules=None):
    """Carrega o playbook do padrão e mescla as tarefas de notificação regulatória
    (mod_ir_<mod>.yaml, cada task com phase_key) por fase — mesmo merge do seeding do plano."""
    core_file = IR_TEMPLATE_FILES.get(standard)
    if not core_file:
        raise ValueError(f"padrão de IR desconhecido: {standard}")
    core = _load_yaml(core_file)
    phases = {p["key"]: p for p in core["phases"]}
    for p in phases.values():
        p.setdefault("tasks", [])
    for mod in modules or []:
        fname = f"mod_ir_{mod}.yaml"
        if not (PLAYBOOKS_DIR / fname).exists():
            continue
        m = _load_yaml(fname)
        for t in m.get("tasks", []):
            pk = t.get("phase_key")
            if pk in phases:
                phases[pk]["tasks"].append(t)
    return core


@transaction.atomic
def seed_incident_plan(incident, standard="nist-800-61", modules=None, anchor=None):
    """Semeia (idempotente) o runbook no incidente. anchor = t0 (detecção/reporte)."""
    anchor = anchor or incident.reported_at or incident.occurred_at or now()
    if modules is None:
        from .regulatory import resolve_regulator_modules

        modules = resolve_regulator_modules(incident)

    playbook = load_ir_playbook(standard, modules)

    plan, _created = IncidentResponsePlan.objects.get_or_create(
        incident=incident,
        defaults={"standard": standard, "anchor_date": anchor, "modules": modules},
    )
    plan.standard = standard
    plan.modules = modules
    if plan.anchor_date is None:
        plan.anchor_date = anchor
    plan.save()

    created_ac = 0
    created_tasks = 0
    for phase_data in playbook["phases"]:
        phase, _ = IncidentPhase.objects.get_or_create(
            incident=incident,
            order=phase_data["order"],
            defaults={
                "name": phase_data["name"],
                "day_start": phase_data.get("day_start", 0),
                "day_end": phase_data.get("day_end", 1),
                "objective": phase_data.get("objective", ""),
            },
        )
        for i, task in enumerate(phase_data.get("tasks", [])):
            tkey = f"{standard}:{task['key']}"
            if IncidentResponseTask.objects.filter(
                incident=incident, template_key=tkey
            ).exists():
                continue
            offset = int(task.get("offset_start_days", 0))
            dur = int(task.get("duration_days", 1))
            ac = AppliedControl.objects.create(
                folder=incident.folder,
                name=task["name"],
                description=task.get("description", ""),
                priority=task.get("priority"),
                effort=task.get("effort"),
                status="to_do",
                start_date=(anchor + timedelta(days=offset)).date(),
                eta=(anchor + timedelta(days=offset + dur)).date(),
            )
            incident.applied_controls.add(ac)
            created_ac += 1
            IncidentResponseTask.objects.create(
                incident=incident,
                phase=phase,
                applied_control=ac,
                estimated_hours=task.get("estimated_hours"),
                order=i,
                template_key=tkey,
            )
            created_tasks += 1
    return {"applied_controls": created_ac, "response_tasks": created_tasks}
