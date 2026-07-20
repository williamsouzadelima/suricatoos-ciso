"""Serializers do app delivery. Nomes seguem <Model>Read/WriteSerializer (resolvidos pelo
SerializerFactory do BaseModelViewSet). Relacionamentos de leitura via FieldsRelatedField."""
from rest_framework import serializers

from core.serializers import BaseModelSerializer
from core.serializer_fields import FieldsRelatedField

from .models import (
    Engagement,
    ClientIntake,
    EngagementPhase,
    PlanTask,
    TimeEntry,
)
from .services.eisenhower import derive_eisenhower

# campos "seguros" do AppliedControl que o seed sempre popula
_AC_FIELDS = ["id", "name", "status", "priority", "effort", "start_date", "eta", "folder"]


# ---------- Engagement ----------
class EngagementReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    perimeter = FieldsRelatedField()
    estimated_hours_total = serializers.ReadOnlyField()
    logged_hours_total = serializers.ReadOnlyField()

    class Meta:
        model = Engagement
        fields = "__all__"


class EngagementWriteSerializer(BaseModelSerializer):
    class Meta:
        model = Engagement
        fields = "__all__"


# ---------- ClientIntake ----------
class ClientIntakeReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    engagement = FieldsRelatedField()
    primary_frameworks = FieldsRelatedField(many=True)

    class Meta:
        model = ClientIntake
        fields = "__all__"


class ClientIntakeWriteSerializer(BaseModelSerializer):
    class Meta:
        model = ClientIntake
        fields = "__all__"


# ---------- EngagementPhase ----------
class EngagementPhaseReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    engagement = FieldsRelatedField()
    organisation_objective = FieldsRelatedField()
    date_start = serializers.DateField(read_only=True)
    date_end = serializers.DateField(read_only=True)
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = EngagementPhase
        fields = "__all__"

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class EngagementPhaseWriteSerializer(BaseModelSerializer):
    class Meta:
        model = EngagementPhase
        fields = "__all__"


# ---------- PlanTask (ponte + Eisenhower) ----------
class PlanTaskReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    engagement = FieldsRelatedField()
    phase = FieldsRelatedField(["id", "name", "order"])
    applied_control = FieldsRelatedField(_AC_FIELDS)
    task_template = FieldsRelatedField()
    eisenhower = serializers.SerializerMethodField()

    class Meta:
        model = PlanTask
        fields = "__all__"

    def get_eisenhower(self, obj):
        horizon = int(self.context.get("horizon_days") or 21)
        return derive_eisenhower(obj, horizon_days=horizon)


class PlanTaskWriteSerializer(BaseModelSerializer):
    class Meta:
        model = PlanTask
        fields = "__all__"


# ---------- TimeEntry (Fase 2) ----------
class TimeEntryReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    engagement = FieldsRelatedField()
    plan_task = FieldsRelatedField()
    applied_control = FieldsRelatedField(_AC_FIELDS)
    user = FieldsRelatedField()

    class Meta:
        model = TimeEntry
        fields = "__all__"


class TimeEntryWriteSerializer(BaseModelSerializer):
    class Meta:
        model = TimeEntry
        fields = "__all__"
