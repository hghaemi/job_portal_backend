from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import JobApplicationViewSet

router = DefaultRouter()
router.register("", JobApplicationViewSet, basename="job-application")

urlpatterns = [
    path("", include(router.urls)),
]
