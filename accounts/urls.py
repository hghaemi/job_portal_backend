from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    MeView,
    ChangePasswordView,
    JobSeekerProfileView,
    CompanyProfileView,
    CompanyPublicDetailView,
)

urlpatterns = [
    # auth
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="auth-logout"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("auth/me/", MeView.as_view(), name="auth-me"),

    # profiles
    path("profile/jobseeker/", JobSeekerProfileView.as_view(), name="jobseeker-profile"),
    path("profile/company/", CompanyProfileView.as_view(), name="company-profile"),
    path("companies/<int:pk>/", CompanyPublicDetailView.as_view(), name="company-public-detail"),
]
