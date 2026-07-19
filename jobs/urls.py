from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import JobCategoryViewSet, JobPostingViewSet, CompanyJobPostingListView

router = DefaultRouter()
router.register("categories", JobCategoryViewSet, basename="job-category")
router.register("", JobPostingViewSet, basename="job-posting")

urlpatterns = [
    path("companies/<int:company_id>/", CompanyJobPostingListView.as_view(), name="company-jobs"),
    path("", include(router.urls)),
]
