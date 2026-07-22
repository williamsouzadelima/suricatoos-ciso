"""vCISO Delivery — modelos aditivos (app `delivery`).

Camada de entrega/onboarding vCISO SOBRE os modelos existentes do CISO Assistant, sem
modificar nada do upstream. A "tarefa" canônica do plano continua sendo `core.AppliedControl`
(que o Kanban/my-assignments/calendar/Gantt já renderizam); este app adiciona apenas a
camada de engajamento/fase/horas/Eisenhower via relação (FK), nunca por campo novo no core.
"""
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from iam.models import FolderMixin, User
from core.base_models import AbstractBaseModel, NameDescriptionMixin
from .taxonomy import sector_choices, subsector_choices
from core.models import (
    AppliedControl,
    Perimeter,
    Asset,
    Incident,
    Actor,
    Evidence,
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
    day_zero = models.DateField(
        null=True, blank=True, verbose_name=_("Day zero (plan anchor)")
    )
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
    website = models.CharField(
        max_length=255, blank=True,
        verbose_name=_("Client website/domain"),
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

    engagement = models.ForeignKey(
        Engagement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intakes",
    )
    company_name = models.CharField(max_length=255, blank=True)
    sector = models.CharField(max_length=40, choices=sector_choices(), blank=True)
    subsector = models.CharField(
        max_length=60, choices=subsector_choices(), blank=True
    )
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
    """Ponte: camada fase/horas/Eisenhower sobre a tarefa real (AppliedControl)."""

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


class BusinessCatalog(NameDescriptionMixin, FolderMixin):
    """Catálogo de negócio (capacidade/serviço) do cliente, com parâmetros para calcular o
    prejuízo de indisponibilidade. Dependências tecnológicas + custos: ver CatalogDependency."""

    class Criticality(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    class Currency(models.TextChoices):
        EUR = "€", "Euro (€)"
        BRL = "R$", "Real (R$)"
        USD = "$", "Dólar (US$)"
        GBP = "£", "Libra (£)"
        CHF = "CHF", "Franco suíço (CHF)"
        AUD = "A$", "Dólar australiano (A$)"
        CAD = "C$", "Dólar canadense (C$)"
        JPY = "¥", "Iene (¥)"
        MXN = "MX$", "Peso mexicano (MX$)"
        ZAR = "ZAR", "Rand (ZAR)"

    engagement = models.ForeignKey(
        Engagement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalogs",
    )
    ref_id = models.CharField(max_length=100, blank=True)
    criticality = models.CharField(
        max_length=20,
        choices=Criticality.choices,
        default=Criticality.MEDIUM,
        verbose_name=_("Criticality"),
    )
    currency = models.CharField(
        max_length=8,
        blank=True,
        default="",
        choices=Currency.choices,
        verbose_name=_("Currency (blank = global default)"),
    )
    collaborators = models.PositiveIntegerField(
        default=0, verbose_name=_("Collaborators using the catalog")
    )
    collaborator_hourly_cost = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Collaborator hourly cost (fallback: global daily rate / 8)"),
    )
    hourly_revenue = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Hourly revenue generated"),
    )
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Profit margin (%) for lost profit"),
    )
    regulatory_hourly = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Regulatory penalty per hour"),
    )
    regulatory_fixed = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Fixed regulatory penalty per incident"),
    )
    maintenance_extra_annual = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Extra annual maintenance cost (beyond dependencies)"),
    )

    class Meta:
        verbose_name = _("Business catalog")
        verbose_name_plural = _("Business catalogs")

    def save(self, *args, **kwargs):
        if self.engagement_id and self.engagement.folder_id:
            self.folder = self.engagement.folder
        super().save(*args, **kwargs)

    @property
    def maintenance_annual_total(self):
        deps = self.dependencies.aggregate(total=models.Sum("annual_cost"))["total"] or 0
        return float(deps) + float(self.maintenance_extra_annual or 0)


class CatalogDependency(AbstractBaseModel, FolderMixin):
    """Dependência tecnológica de um catálogo + seu custo anual de manutenção."""

    catalog = models.ForeignKey(
        BusinessCatalog, on_delete=models.CASCADE, related_name="dependencies"
    )
    name = models.CharField(max_length=255, verbose_name=_("Dependency name"))
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_catalog_deps",
    )
    annual_cost = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name=_("Annual maintenance cost"),
    )
    observation = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Catalog dependency")
        verbose_name_plural = _("Catalog dependencies")

    def save(self, *args, **kwargs):
        if self.catalog_id and self.catalog.folder_id:
            self.folder = self.catalog.folder
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Incident Response (IR) — camada de ORQUESTRAÇÃO sobre core.Incident.
# Nada em core/resilience é modificado: todo vínculo é FK *para dentro* do core
# (mesmo padrão de resilience.DoraIncidentReport.incident). A "atividade" real de
# resposta continua sendo core.AppliedControl (Kanban/Gantt); a evidência continua
# sendo core.Evidence via core.TimelineEntry.evidences.
# ---------------------------------------------------------------------------


class IncidentResponsePlan(AbstractBaseModel, FolderMixin):
    """Cabeçalho do plano de resposta de UM incidente (1:1). Guarda o padrão/âncora/
    módulos regulatórios e a narrativa que alimenta o PIR."""

    class Standard(models.TextChoices):
        NIST_800_61 = "nist-800-61", "NIST SP 800-61"
        ISO_27035 = "iso-27035", "ISO/IEC 27035"

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        CLOSED = "closed", _("Closed")

    incident = models.OneToOneField(
        Incident, on_delete=models.CASCADE, related_name="response_plan"
    )
    engagement = models.ForeignKey(
        Engagement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incident_response_plans",
    )
    standard = models.CharField(
        max_length=20, choices=Standard.choices, default=Standard.NIST_800_61
    )
    anchor_date = models.DateTimeField(null=True, blank=True)
    modules = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    exec_summary = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Incident response plan")
        verbose_name_plural = _("Incident response plans")

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
            if self.anchor_date is None:
                self.anchor_date = self.incident.reported_at or self.incident.occurred_at
            if self.engagement_id is None:
                self.engagement = (
                    Engagement.objects.filter(folder=self.incident.folder)
                    .order_by("-created_at")
                    .first()
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"IRP · {self.incident.name}"


class IncidentPhase(NameDescriptionMixin, FolderMixin):
    """Fase do runbook (espelha EngagementPhase). day_start/day_end são dias relativos
    ao anchor do incidente (t0 = detecção/reporte)."""

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="ir_phases"
    )
    order = models.PositiveSmallIntegerField(default=0)
    day_start = models.SmallIntegerField(default=0)
    day_end = models.SmallIntegerField(default=1)
    objective = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Incident phase")
        verbose_name_plural = _("Incident phases")

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class IncidentResponseTask(AbstractBaseModel, FolderMixin):
    """Ponte: fase/horas sobre a atividade real de resposta (core.AppliedControl,
    também adicionada a incident.applied_controls). Espelha PlanTask."""

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="ir_tasks"
    )
    phase = models.ForeignKey(
        IncidentPhase, on_delete=models.CASCADE, related_name="tasks"
    )
    applied_control = models.ForeignKey(
        AppliedControl,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ir_task",
    )
    estimated_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    order = models.PositiveSmallIntegerField(default=0)
    template_key = models.CharField(max_length=150, blank=True, db_index=True)

    class Meta:
        ordering = ["phase__order", "order"]
        verbose_name = _("Incident response task")
        verbose_name_plural = _("Incident response tasks")
        constraints = [
            models.UniqueConstraint(
                fields=["incident", "template_key"],
                condition=~models.Q(template_key=""),
                name="unique_irtask_template_key_per_incident",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    def __str__(self):
        if self.applied_control_id:
            return self.applied_control.name
        return str(self.id)


class IncidentRole(AbstractBaseModel, FolderMixin):
    """Papel/RACI no incidente (além de Incident.owners). Reusa Actor (user|team|entity)."""

    class Role(models.TextChoices):
        INCIDENT_COMMANDER = "incident_commander", _("Incident commander")
        COMMS_LEAD = "comms_lead", _("Communications lead")
        TECH_FORENSICS = "tech_forensics", _("Technical / forensics")
        LEGAL_DPO = "legal_dpo", _("Legal / DPO")
        SCRIBE = "scribe", _("Scribe")
        EXEC_SPONSOR = "exec_sponsor", _("Executive sponsor")
        LIAISON = "liaison", _("Liaison")

    class Raci(models.TextChoices):
        RESPONSIBLE = "responsible", _("Responsible")
        ACCOUNTABLE = "accountable", _("Accountable")
        CONSULTED = "consulted", _("Consulted")
        INFORMED = "informed", _("Informed")

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="ir_roles"
    )
    actor = models.ForeignKey(
        Actor, on_delete=models.PROTECT, related_name="ir_roles"
    )
    role = models.CharField(max_length=30, choices=Role.choices)
    raci = models.CharField(
        max_length=15, choices=Raci.choices, default=Raci.RESPONSIBLE
    )
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Incident role")
        verbose_name_plural = _("Incident roles")

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_role_display()} ({self.get_raci_display()})"


class IncidentStakeholder(AbstractBaseModel, FolderMixin):
    """Matriz de comunicação: quem é informado/consultado, por qual canal e cadência."""

    class Party(models.TextChoices):
        INTERNAL = "internal", _("Internal")
        CUSTOMER = "customer", _("Customer")
        REGULATOR = "regulator", _("Regulator")
        VENDOR = "vendor", _("Vendor")
        PARTNER = "partner", _("Partner")
        MEDIA = "media", _("Media / press")
        LAW_ENFORCEMENT = "law_enforcement", _("Law enforcement")

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="ir_stakeholders"
    )
    name = models.CharField(max_length=255)
    party = models.CharField(
        max_length=20, choices=Party.choices, default=Party.INTERNAL
    )
    actor = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ir_stakeholders",
    )
    channel = models.CharField(max_length=120, blank=True)
    cadence = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Incident stakeholder")
        verbose_name_plural = _("Incident stakeholders")

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RegulatoryNotification(AbstractBaseModel, FolderMixin):
    """Rastreador de obrigação de notificação regulatória por incidente. deadline_hours
    NULL = obrigação qualitativa (norma diz "tempestivo/assim que ciente" — não hora fixa)."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUBMITTED = "submitted", _("Submitted")
        ACKNOWLEDGED = "acknowledged", _("Acknowledged")
        NOT_APPLICABLE = "not_applicable", _("Not applicable")

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="ir_notifications"
    )
    regulator = models.CharField(max_length=80)
    module_key = models.CharField(max_length=40, blank=True)
    obligation_ref = models.CharField(max_length=255, blank=True)
    deadline_hours = models.PositiveIntegerField(null=True, blank=True)
    qualitative_note = models.TextField(blank=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    channel = models.CharField(max_length=120, blank=True)
    template_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    evidences = models.ManyToManyField(
        Evidence, blank=True, related_name="ir_notifications"
    )

    class Meta:
        verbose_name = _("Regulatory notification")
        verbose_name_plural = _("Regulatory notifications")
        constraints = [
            models.UniqueConstraint(
                fields=["incident", "module_key", "obligation_ref"],
                name="unique_regnotif_per_incident_module_ref",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return (
            self.status == self.Status.PENDING
            and self.due_at is not None
            and self.due_at < now()
        )

    def __str__(self):
        return f"{self.regulator} · {self.obligation_ref}"


class IncidentCost(AbstractBaseModel, FolderMixin):
    """Linhas manuais do P&L do incidente (esforço de resposta e impacto de negócio são
    COMPUTADOS por services/incident_cost.py, nunca armazenados). 1:1 com o incidente."""

    incident = models.OneToOneField(
        Incident, on_delete=models.CASCADE, related_name="ir_cost"
    )
    currency = models.CharField(
        max_length=8,
        blank=True,
        default="",
        verbose_name=_("Currency (blank = global default)"),
    )
    vendor_forensics = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True
    )
    vendor_legal = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True
    )
    other_external = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True
    )
    regulatory_fines = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True
    )
    downtime_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Incident cost")
        verbose_name_plural = _("Incident costs")

    def save(self, *args, **kwargs):
        if self.incident_id:
            self.folder = self.incident.folder
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cost · {self.incident.name}"


auditlog.register(Engagement)
auditlog.register(ClientIntake)
auditlog.register(EngagementPhase)
auditlog.register(PlanTask)
auditlog.register(TimeEntry)
auditlog.register(BusinessCatalog)
auditlog.register(CatalogDependency)
auditlog.register(IncidentResponsePlan)
auditlog.register(IncidentPhase)
auditlog.register(IncidentResponseTask)
auditlog.register(IncidentRole)
auditlog.register(IncidentStakeholder)
auditlog.register(RegulatoryNotification)
auditlog.register(IncidentCost)
