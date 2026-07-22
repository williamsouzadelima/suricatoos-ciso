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
    BusinessCatalog,
    CatalogDependency,
    IncidentResponsePlan,
    IncidentPhase,
    IncidentResponseTask,
    IncidentRole,
    IncidentStakeholder,
    RegulatoryNotification,
    IncidentCost,
    IncidentTimeEntry,
)
from .services.eisenhower import derive_eisenhower

# campos "seguros" do AppliedControl que o seed sempre popula
_AC_FIELDS = ["id", "name", "status", "priority", "effort", "start_date", "eta", "folder", "progress_field"]


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


# ---------- Catálogos de negócio ----------
class BusinessCatalogReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    engagement = FieldsRelatedField()
    maintenance_annual_total = serializers.ReadOnlyField()

    class Meta:
        model = BusinessCatalog
        fields = "__all__"


class BusinessCatalogWriteSerializer(BaseModelSerializer):
    class Meta:
        model = BusinessCatalog
        fields = "__all__"


class CatalogDependencyReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    catalog = FieldsRelatedField()
    asset = FieldsRelatedField()

    class Meta:
        model = CatalogDependency
        fields = "__all__"


class CatalogDependencyWriteSerializer(BaseModelSerializer):
    class Meta:
        model = CatalogDependency
        fields = "__all__"


# ---------- Resposta a Incidentes (IR) ----------
class IncidentResponsePlanReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    engagement = FieldsRelatedField()

    class Meta:
        model = IncidentResponsePlan
        fields = "__all__"


class IncidentResponsePlanWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentResponsePlan
        fields = "__all__"


class IncidentPhaseReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = IncidentPhase
        fields = "__all__"

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class IncidentPhaseWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentPhase
        fields = "__all__"


class IncidentResponseTaskReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    phase = FieldsRelatedField(["id", "name", "order"])
    applied_control = FieldsRelatedField(_AC_FIELDS)

    class Meta:
        model = IncidentResponseTask
        fields = "__all__"


class IncidentResponseTaskWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentResponseTask
        fields = "__all__"


class IncidentRoleReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    actor = FieldsRelatedField()

    class Meta:
        model = IncidentRole
        fields = "__all__"


class IncidentRoleWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentRole
        fields = "__all__"


class IncidentStakeholderReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    actor = FieldsRelatedField()

    class Meta:
        model = IncidentStakeholder
        fields = "__all__"


class IncidentStakeholderWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentStakeholder
        fields = "__all__"


class RegulatoryNotificationReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    evidences = FieldsRelatedField(many=True)
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = RegulatoryNotification
        fields = "__all__"


class RegulatoryNotificationWriteSerializer(BaseModelSerializer):
    class Meta:
        model = RegulatoryNotification
        fields = "__all__"


class IncidentCostReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()

    class Meta:
        model = IncidentCost
        fields = "__all__"


class IncidentCostWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentCost
        fields = "__all__"


class IncidentTimeEntryReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    incident = FieldsRelatedField()
    applied_control = FieldsRelatedField(_AC_FIELDS)
    user = FieldsRelatedField()

    class Meta:
        model = IncidentTimeEntry
        fields = "__all__"


class IncidentTimeEntryWriteSerializer(BaseModelSerializer):
    class Meta:
        model = IncidentTimeEntry
        fields = "__all__"
