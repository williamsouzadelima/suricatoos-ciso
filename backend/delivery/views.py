"""ViewSets do app delivery. Herdam BaseModelViewSet (filtro RBAC por folder de graça).
O shim local aponta serializers_module para 'delivery.serializers'."""
from collections import Counter
from datetime import timedelta
from wsgiref.util import FileWrapper

from django.db.models import Sum, Count
from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from core.views import BaseModelViewSet as AbstractBaseModelViewSet
from iam.models import RoleAssignment
from core.models import Asset

from .models import Engagement, ClientIntake, EngagementPhase, PlanTask, TimeEntry
from .serializers import PlanTaskReadSerializer
from .services.seeding import seed_engagement_plan
from .services.provisioning import create_client_folder
from .services.eisenhower import derive_eisenhower

# rótulos amigáveis das roles builtin (codename -> pt-BR)
ROLE_LABELS = {
    "BI-RL-ADM": "Administrador",
    "BI-RL-DMA": "Gestor do domínio",
    "BI-RL-ANA": "Analista",
    "BI-RL-APP": "Aprovador",
    "BI-RL-AUD": "Leitor",
    "BI-RL-TPR": "Terceiro",
    "BI-RL-ADE": "Auditado",
}


class BaseModelViewSet(AbstractBaseModelViewSet):
    serializers_module = "delivery.serializers"


class EngagementViewSet(BaseModelViewSet):
    model = Engagement
    filterset_fields = ["folder", "perimeter", "status", "hours_model"]

    @action(detail=False, name="Get hours model choices")
    def hours_model(self, request):
        return Response(dict(Engagement.HoursModel.choices))

    @action(detail=False, name="Get status choices")
    def status(self, request):
        return Response(dict(Engagement.Status.choices))

    @action(detail=True, methods=["get"], name="Capacity vs contracted hours")
    def capacity(self, request, pk):
        eng = self.get_object()
        contracted = float(eng.contracted_hours) if eng.contracted_hours is not None else None
        estimated = float(eng.estimated_hours_total)
        by_phase = []
        for ph in eng.phases.all().order_by("order"):
            agg = ph.tasks.aggregate(h=Sum("estimated_hours"), n=Count("id"))
            by_phase.append(
                {
                    "phase": str(ph.id),
                    "name": ph.name,
                    "order": ph.order,
                    "estimated_hours": float(agg["h"] or 0),
                    "task_count": agg["n"],
                }
            )
        return Response(
            {
                "hours_model": eng.hours_model,
                "contracted_hours": contracted,
                "estimated_hours": estimated,
                "logged_hours": float(eng.logged_hours_total),
                "remaining_vs_contracted": (contracted - estimated)
                if contracted is not None
                else None,
                "utilization_pct": round(estimated / contracted * 100, 1)
                if contracted
                else None,
                "over_budget": contracted is not None and estimated > contracted,
                "by_phase": by_phase,
            }
        )

    @action(detail=True, methods=["get"], name="Engagement dashboard")
    def dashboard(self, request, pk):
        eng = self.get_object()
        horizon = int(request.query_params.get("horizon_days") or 21)
        tasks = list(eng.plan_tasks.select_related("applied_control", "phase"))
        status_counter = Counter()
        quad_counter = Counter()
        for pt in tasks:
            if pt.applied_control:
                status_counter[pt.applied_control.status] += 1
            quad_counter[derive_eisenhower(pt, horizon_days=horizon)["quadrant"]] += 1
        phases = []
        for ph in eng.phases.all().order_by("order"):
            ph_tasks = [pt for pt in tasks if pt.phase_id == ph.id]
            done = sum(
                1
                for pt in ph_tasks
                if pt.applied_control and pt.applied_control.status == "active"
            )
            phases.append(
                {
                    "phase": str(ph.id),
                    "name": ph.name,
                    "order": ph.order,
                    "date_start": ph.date_start,
                    "date_end": ph.date_end,
                    "task_count": len(ph_tasks),
                    "done_count": done,
                    "estimated_hours": float(sum((pt.estimated_hours or 0) for pt in ph_tasks)),
                }
            )
        contracted = float(eng.contracted_hours) if eng.contracted_hours is not None else None
        estimated = float(eng.estimated_hours_total)
        return Response(
            {
                "engagement": str(eng.id),
                "name": eng.name,
                "status": eng.status,
                "day_zero": eng.day_zero,
                "hours": {
                    "contracted": contracted,
                    "estimated": estimated,
                    "logged": float(eng.logged_hours_total),
                    "over_budget": contracted is not None and estimated > contracted,
                },
                "kanban_status": dict(status_counter),
                "eisenhower": dict(quad_counter),
                "phases": phases,
            }
        )

    @action(detail=True, methods=["get"], name="Burn-down of logged hours")
    def burn_down(self, request, pk):
        eng = self.get_object()
        budget = float(eng.contracted_hours) if eng.contracted_hours is not None else None
        day_zero = eng.day_zero
        day_end = (day_zero + timedelta(days=100)) if day_zero else None
        entries = (
            TimeEntry.objects.filter(engagement=eng)
            .order_by("date")
            .values("date", "hours")
        )
        actual = []
        cum = 0.0
        if budget is not None and day_zero:
            actual.append([day_zero.isoformat(), budget])  # início: orçamento cheio restante
        for e in entries:
            cum += float(e["hours"])
            d = e["date"].isoformat()
            actual.append([d, max(budget - cum, 0) if budget is not None else cum])
        ideal = None
        if budget is not None and day_zero and day_end:
            ideal = [[day_zero.isoformat(), budget], [day_end.isoformat(), 0]]
        return Response(
            {
                "budget": budget,
                "hours_model": eng.hours_model,
                "day_zero": day_zero.isoformat() if day_zero else None,
                "day_end": day_end.isoformat() if day_end else None,
                "logged_total": float(eng.logged_hours_total),
                "actual": actual,
                "ideal": ideal,
                "mode": "burndown" if budget is not None else "burnup",
            }
        )

    @action(detail=True, methods=["get"], name="Team and resources")
    def team_resources(self, request, pk):
        eng = self.get_object()
        folder = eng.folder
        team = []
        ras = (
            RoleAssignment.objects.filter(perimeter_folders=folder)
            .select_related("user", "user_group", "role")
            .distinct()
        )
        for ra in ras:
            role_label = ROLE_LABELS.get(ra.role.name, ra.role.name) if ra.role_id else "—"
            if ra.user_id:
                team.append(
                    {"kind": "user", "name": ra.user.email, "role": role_label}
                )
            elif ra.user_group_id:
                team.append(
                    {"kind": "group", "name": ra.user_group.name, "role": role_label}
                )
        resources = [
            {
                "id": str(a.id),
                "name": a.name,
                "type": a.get_type_display(),
                "description": a.description or "",
            }
            for a in Asset.objects.filter(folder=folder).order_by("name")
        ]
        return Response(
            {
                "folder_id": str(folder.id),
                "team": team,
                "team_count": len(team),
                "resources": resources,
                "resources_count": len(resources),
            }
        )

    @action(detail=True, methods=["get"], name="Engagement PPTX report")
    def report_pptx(self, request, pk):
        from .pptx_engagement import build_engagement_pptx

        eng = self.get_object()
        prefs = getattr(request.user, "preferences", None) or {}
        lang = prefs.get("lang", "pt") if isinstance(prefs, dict) else "pt"
        if lang not in ("pt", "en", "fr"):
            lang = "pt"
        buf = build_engagement_pptx(eng, lang)
        safe = "".join(
            c if c.isalnum() or c in ".-_" else "_" for c in (eng.folder.name or "engajamento")
        )
        resp = StreamingHttpResponse(
            FileWrapper(buf),
            content_type=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
        )
        resp["Content-Disposition"] = f'attachment; filename="engajamento-{safe}.pptx"'
        return resp

    @action(detail=True, methods=["post"], name="Seed the 100-day plan")
    def seed_plan(self, request, pk):
        eng = self.get_object()
        template = request.data.get("template", "vciso-100d")
        modules = request.data.get("modules", [])
        if isinstance(modules, str):
            modules = [m.strip() for m in modules.split(",") if m.strip()]
        day_zero = request.data.get("day_zero")
        if day_zero and not eng.day_zero:
            eng.day_zero = day_zero
            eng.save(update_fields=["day_zero"])
        if not eng.day_zero:
            return Response(
                {"detail": "day_zero é obrigatório antes de semear o plano."}, status=400
            )
        result = seed_engagement_plan(eng, template=template, modules=modules)
        return Response(result)


class ClientIntakeViewSet(BaseModelViewSet):
    model = ClientIntake
    filterset_fields = ["folder", "engagement", "subsector", "provisioning_status"]

    @action(detail=False, name="Get subsector choices")
    def subsector(self, request):
        return Response(dict(ClientIntake.Subsector.choices))

    @action(detail=True, methods=["post"], name="Provision client structure")
    def provision(self, request, pk):
        intake = self.get_object()
        folder, _ = create_client_folder(intake.company_name or intake.name)
        eng = intake.engagement
        if eng is None:
            eng = Engagement.objects.create(
                folder=folder,
                name=f"Engajamento vCISO — {folder.name}",
                status=Engagement.Status.ONBOARDING,
            )
            intake.engagement = eng
        intake.provisioning_status = ClientIntake.Provisioning.PROVISIONED
        intake.provisioned_at = timezone.now()
        intake.save(
            update_fields=["engagement", "provisioning_status", "provisioned_at"]
        )
        return Response({"engagement": str(eng.id), "folder": str(folder.id)})


class EngagementPhaseViewSet(BaseModelViewSet):
    model = EngagementPhase
    filterset_fields = ["folder", "engagement", "order"]


class PlanTaskViewSet(BaseModelViewSet):
    model = PlanTask
    filterset_fields = [
        "engagement",
        "phase",
        "folder",
        "applied_control",
        "task_template",
    ]
    search_fields = ["template_key"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["horizon_days"] = self.request.query_params.get("horizon_days") or 21
        return ctx

    @action(detail=False, methods=["get"], name="Eisenhower matrix")
    def eisenhower(self, request):
        qs = self.filter_queryset(self.get_queryset()).select_related(
            "applied_control", "phase"
        )
        horizon = int(request.query_params.get("horizon_days") or 21)
        ctx = self.get_serializer_context()
        buckets = {"do": [], "schedule": [], "delegate": [], "eliminate": []}
        for pt in qs:
            data = PlanTaskReadSerializer(pt, context=ctx).data
            buckets[data["eisenhower"]["quadrant"]].append(data)
        return Response({"horizon_days": horizon, "quadrants": buckets})

    @action(detail=False, methods=["post"], name="Reorder plan tasks")
    def reorder(self, request):
        items = request.data.get("items", [])
        accessible = set(
            str(i) for i in self.get_queryset().values_list("id", flat=True)
        )
        updated = 0
        for it in items:
            tid = str(it.get("id"))
            if tid not in accessible:
                continue
            fields = []
            pt = PlanTask.objects.get(id=tid)
            if "order" in it:
                pt.order = it["order"]
                fields.append("order")
            if it.get("phase"):
                pt.phase_id = it["phase"]
                fields.append("phase")
            if fields:
                pt.save(update_fields=fields)
                updated += 1
        return Response({"updated": updated})


class TimeEntryViewSet(BaseModelViewSet):
    model = TimeEntry
    filterset_fields = ["folder", "engagement", "plan_task", "applied_control", "user", "billable"]
