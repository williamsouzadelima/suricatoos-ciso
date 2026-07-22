from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EngagementViewSet,
    ClientIntakeViewSet,
    EngagementPhaseViewSet,
    PlanTaskViewSet,
    TimeEntryViewSet,
    BusinessCatalogViewSet,
    CatalogDependencyViewSet,
    IncidentResponsePlanViewSet,
    IncidentPhaseViewSet,
    IncidentResponseTaskViewSet,
    IncidentRoleViewSet,
    IncidentStakeholderViewSet,
    RegulatoryNotificationViewSet,
    IncidentCostViewSet,
)

router = DefaultRouter()
router.register(r"engagements", EngagementViewSet, basename="engagements")
router.register(r"client-intakes", ClientIntakeViewSet, basename="client-intakes")
router.register(r"plan-phases", EngagementPhaseViewSet, basename="plan-phases")
router.register(r"plan-tasks", PlanTaskViewSet, basename="plan-tasks")
router.register(r"time-entries", TimeEntryViewSet, basename="time-entries")
router.register(r"business-catalogs", BusinessCatalogViewSet, basename="business-catalogs")
router.register(r"catalog-dependencies", CatalogDependencyViewSet, basename="catalog-dependencies")
router.register(r"incident-response-plans", IncidentResponsePlanViewSet, basename="incident-response-plans")
router.register(r"incident-phases", IncidentPhaseViewSet, basename="incident-phases")
router.register(r"incident-response-tasks", IncidentResponseTaskViewSet, basename="incident-response-tasks")
router.register(r"incident-roles", IncidentRoleViewSet, basename="incident-roles")
router.register(r"incident-stakeholders", IncidentStakeholderViewSet, basename="incident-stakeholders")
router.register(r"regulatory-notifications", RegulatoryNotificationViewSet, basename="regulatory-notifications")
router.register(r"incident-costs", IncidentCostViewSet, basename="incident-costs")

urlpatterns = [
    path("", include(router.urls)),
]
