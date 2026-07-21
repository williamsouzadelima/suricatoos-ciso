"""vCISO Delivery — modelos aditivos (app `delivery`).

Camada de entrega/onboarding vCISO SOBRE os modelos existentes do CISO Assistant, sem
modificar nada do upstream. A "tarefa" canônica do plano continua sendo `core.AppliedControl`
(que o Kanban/my-assignments/calendar/Gantt já renderizam); este app adiciona apenas a
camada de engajamento/fase/horas/Eisenhower via relação (FK), nunca por campo novo no core.
"""
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from iam.models import FolderMixin, User
from core.base_models import AbstractBaseModel, NameDescriptionMixin
from core.models import (
    AppliedControl,
    TaskTemplate,
    Perimeter,
    OrganisationObjective,
    Framework,
)


class Engagement(NameDescriptionMixin, FolderMixin):
    """Contrato/relacionamento vCISO de um cliente. O `folder` (via FolderMixin) É o domínio
    (DOMAIN) do cliente — o RBAC por-folder do BaseModelViewSet aplica-se naturalmente."""

    class HoursModel(models.TextChoices):
        NONE = "none", _("No hours tracking")
        BUDGET = "budget", _("Budget + capacity")
        TIMELOG = "timelog", _("Time-logging")
        HYBRID = "hybrid", _("Hybrid")

    class Status(models.TextChoices):
        PROSPECT = "prospect", _("Prospect")
        ONBOARDING = "onboarding", _("Onboarding")
        ACTIVE = "active", _("Active")
        PAUSED = "paused", _("Paused")
        OFFBOARDING = "offboarding", _("Offboarding")
        CLOSED = "closed", _("Closed")

    perimeter = models.ForeignKey(
        Perimeter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_engagements",
        verbose_name=_("Perimeter"),
    )
    reference = models.CharField(
        max_length=100, blank=True, verbose_name=_("Contract reference")
    )
    hours_model = models.CharField(
        max_length=20,
        choices=HoursModel.choices,
        default=HoursModel.BUDGET,
        verbose_name=_("Hours model"),
    )
    contracted_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Contracted hours"),
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Hourly rate (override of global daily rate / 8)"),
    )
    day_zero = models.DateField(
        null=True, blank=True, verbose_name=_("Day zero (plan anchor)")
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Start date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End date"))
    sla = models.JSONField(default=dict, blank=True, verbose_name=_("SLA"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ONBOARDING,
        verbose_name=_("Status"),
    )
    logo = models.FileField(
        upload_to="branding/clients/", null=True, blank=True,
        verbose_name=_("Client logo"),
    )

    class Meta:
        verbose_name = _("Engagement")
        verbose_name_plural = _("Engagements")
        constraints = [
            models.UniqueConstraint(
                fields=["folder"],
                condition=models.Q(status="active"),
                name="unique_active_engagement_per_folder",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def estimated_hours_total(self):
        return (
            self.plan_tasks.aggregate(total=models.Sum("estimated_hours"))["total"] or 0
        )

    @property
    def logged_hours_total(self):
        return self.time_entries.aggregate(total=models.Sum("hours"))["total"] or 0


class ClientIntake(NameDescriptionMixin, FolderMixin):
    """Captura de onboarding — existe ANTES da estrutura ser provisionada."""

    class Provisioning(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SUBMITTED = "submitted", _("Submitted")
        PROVISIONED = "provisioned", _("Provisioned")

    class Subsector(models.TextChoices):
        BANK = "bank", _("Bank / credit institution")
        ASSET_MANAGER = "asset_manager", _("Asset manager (ANBIMA)")
        BROKER = "broker", _("Broker / DTVM (CVM)")
        OTHER = "other", _("Other / hybrid")

    engagement = models.ForeignKey(
        Engagement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intakes",
    )
    company_name = models.CharField(max_length=255, blank=True)
    subsector = models.CharField(
        max_length=30, choices=Subsector.choices, blank=True
    )
    industry = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=100, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    primary_frameworks = models.ManyToManyField(
        Framework, blank=True, related_name="delivery_intakes"
    )
    contacts = models.JSONField(default=dict, blank=True)
    answers = models.JSONField(default=dict, blank=True)
    assets_seed = models.JSONField(default=list, blank=True)
    provisioning_status = models.CharField(
        max_length=20, choices=Provisioning.choices, default=Provisioning.DRAFT
    )
    provisioned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Client intake")
        verbose_name_plural = _("Client intakes")

    def __str__(self):
        return self.company_name or self.name


class EngagementPhase(NameDescriptionMixin, FolderMixin):
    """Fase do plano (0-30 / 31-60 / 61-100). Datas derivam de engagement.day_zero."""

    engagement = models.ForeignKey(
        Engagement, on_delete=models.CASCADE, related_name="phases"
    )
    order = models.PositiveSmallIntegerField(default=0)
    day_start = models.PositiveSmallIntegerField(default=0)
    day_end = models.PositiveSmallIntegerField(default=30)
    objective = models.TextField(blank=True)
    organisation_objective = models.ForeignKey(
        OrganisationObjective,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_phases",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = _("Engagement phase")
        verbose_name_plural = _("Engagement phases")

    def save(self, *args, **kwargs):
        if self.engagement_id:
            self.folder = self.engagement.folder
        super().save(*args, **kwargs)

    def _date(self, day):
        if self.engagement.day_zero is None:
            return None
        return self.engagement.day_zero + timedelta(days=day)

    @property
    def date_start(self):
        return self._date(self.day_start)

    @property
    def date_end(self):
        return self._date(self.day_end)

    def __str__(self):
        return self.name


class PlanTask(AbstractBaseModel, FolderMixin):
    """Ponte (o coração do design): camada fase/horas/Eisenhower sobre a tarefa real
    (AppliedControl para tarefas de board, ou TaskTemplate para recorrentes)."""

    engagement = models.ForeignKey(
        Engagement, on_delete=models.CASCADE, related_name="plan_tasks"
    )
    phase = models.ForeignKey(
        EngagementPhase, on_delete=models.CASCADE, related_name="tasks"
    )
    applied_control = models.ForeignKey(
        AppliedControl,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="delivery_plan_task",
    )
    task_template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="delivery_plan_task",
    )
    estimated_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    order = models.PositiveSmallIntegerField(default=0)
    urgency_override = models.SmallIntegerField(null=True, blank=True)
    importance_override = models.SmallIntegerField(null=True, blank=True)
    template_key = models.CharField(max_length=150, blank=True, db_index=True)

    class Meta:
        ordering = ["phase__order", "order"]
        verbose_name = _("Plan task")
        verbose_name_plural = _("Plan tasks")
        constraints = [
            models.CheckConstraint(
                name="plantask_exactly_one_target",
                condition=(
                    models.Q(
                        applied_control__isnull=False, task_template__isnull=True
                    )
                    | models.Q(
                        applied_control__isnull=True, task_template__isnull=False
                    )
                ),
            ),
            models.UniqueConstraint(
                fields=["engagement", "template_key"],
                condition=~models.Q(template_key=""),
                name="unique_plantask_template_key_per_engagement",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.engagement_id:
            self.folder = self.engagement.folder
        super().save(*args, **kwargs)

    def __str__(self):
        if self.applied_control_id:
            return self.applied_control.name
        if self.task_template_id:
            return self.task_template.name
        return str(self.id)


class TimeEntry(AbstractBaseModel, FolderMixin):
    """Time-logging real (Fase 2). Horas gastas por tarefa/pessoa → burn-down."""

    engagement = models.ForeignKey(
        Engagement, on_delete=models.CASCADE, related_name="time_entries"
    )
    plan_task = models.ForeignKey(
        PlanTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    applied_control = models.ForeignKey(
        AppliedControl,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_time_entries",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_time_entries",
    )
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    billable = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Time entry")
        verbose_name_plural = _("Time entries")

    def save(self, *args, **kwargs):
        if self.engagement_id:
            self.folder = self.engagement.folder
        super().save(*args, **kwargs)


auditlog.register(Engagement)
auditlog.register(ClientIntake)
auditlog.register(EngagementPhase)
auditlog.register(PlanTask)
auditlog.register(TimeEntry)
