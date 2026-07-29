from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsCompany, IsJobOwnerCompany

from .models import JobCategory, JobPosting
from .filters import JobPostingFilter
from .serializers import (
    JobCategorySerializer,
    JobPostingListSerializer,
    JobPostingDetailSerializer,
)


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class JobPostingViewSet(viewsets.ModelViewSet):
    filterset_class = JobPostingFilter
    search_fields = ["title", "description", "location"]
    ordering_fields = ["created_at", "salary_min", "salary_max", "application_deadline"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ("create",):
            return [permissions.IsAuthenticated(), IsCompany()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsCompany(), IsJobOwnerCompany()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return JobPostingListSerializer
        return JobPostingDetailSerializer

    def get_queryset(self):
        qs = (
            JobPosting.objects.select_related("company", "company__company_profile", "category")
            .annotate(applications_count=Count("applications"))
        )
        user = self.request.user

        if self.action == "list":
            if self.request.query_params.get("mine") == "1":
                if not getattr(user, "is_company", False):
                    raise PermissionDenied("Only companies can view their own postings.")
                return qs.filter(company=user)

            return qs.filter(status=JobPosting.Status.PUBLISHED).exclude(
                application_deadline__lt=timezone.now().date()
            )

        if getattr(user, "is_company", False):
            return qs.filter(Q(status=JobPosting.Status.PUBLISHED) | Q(company=user))
        return qs.filter(status=JobPosting.Status.PUBLISHED)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)


class CompanyJobPostingListView(generics.ListAPIView):
    serializer_class = JobPostingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.kwargs["company_id"]
        return (
            JobPosting.objects.filter(company_id=company_id, status=JobPosting.Status.PUBLISHED)
            .select_related("company", "company__company_profile", "category")
            .annotate(applications_count=Count("applications"))
        )