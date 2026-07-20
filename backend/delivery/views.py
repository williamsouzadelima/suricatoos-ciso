"""ViewSets do app delivery. Herdam BaseModelViewSet (filtro RBAC por folder de graça).
O shim local aponta serializers_module para 'delivery.serializers'."""
from collections import Counter

from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from core.views import BaseModelViewSet as AbstractBaseModelViewSet

from .models import Engagement, ClientIntake, EngagementPhase, PlanTask, TimeEntry
from .serializers import PlanTaskReadSerializer
from .services.seeding import seed_engagement_plan
from .services.provisioning import create_client_folder
from .services.eisenhower import derive_eisenhower


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
