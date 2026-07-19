from django.urls import path

from .dashboard_views import (
    CompanyDashboardStatsView,
    JobSeekerDashboardStatsView,
    PlatformOverviewStatsView,
)

urlpatterns = [
    path("dashboard/company/", CompanyDashboardStatsView.as_view(), name="dashboard-company"),
    path("dashboard/jobseeker/", JobSeekerDashboardStatsView.as_view(), name="dashboard-jobseeker"),
    path("dashboard/overview/", PlatformOverviewStatsView.as_view(), name="dashboard-overview"),
]
