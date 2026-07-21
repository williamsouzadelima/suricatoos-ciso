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
)

router = DefaultRouter()
router.register(r"engagements", EngagementViewSet, basename="engagements")
router.register(r"client-intakes", ClientIntakeViewSet, basename="client-intakes")
router.register(r"plan-phases", EngagementPhaseViewSet, basename="plan-phases")
router.register(r"plan-tasks", PlanTaskViewSet, basename="plan-tasks")
router.register(r"time-entries", TimeEntryViewSet, basename="time-entries")
router.register(r"business-catalogs", BusinessCatalogViewSet, basename="business-catalogs")
router.register(r"catalog-dependencies", CatalogDependencyViewSet, basename="catalog-dependencies")

urlpatterns = [
    path("", include(router.urls)),
]
