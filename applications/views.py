from rest_framework import viewsets, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.permissions import IsJobSeeker, IsCompany

from jobs.models import JobPosting

from .models import JobApplication, ApplicationStatusHistory
from .serializers import (
    JobApplicationCreateSerializer,
    JobApplicationListSerializer,
    JobApplicationDetailSerializer,
    ApplicationStatusUpdateSerializer,
)


class JobApplicationViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsJobSeeker()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return JobApplicationCreateSerializer
        if self.action == "list":
            return JobApplicationListSerializer
        if self.action in ("partial_update", "update"):
            return ApplicationStatusUpdateSerializer
        return JobApplicationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        base = JobApplication.objects.select_related("job", "applicant", "job__company")

        if getattr(user, "is_jobseeker", False):
            qs = base.filter(applicant=user)
            job_id = self.request.query_params.get("job")
            if job_id:
                qs = qs.filter(job_id=job_id)
            return qs
        if getattr(user, "is_company", False):
            qs = base.filter(job__company=user)
            job_id = self.request.query_params.get("job")
            if job_id:
                qs = qs.filter(job_id=job_id)
            return qs
        return base.none()

    def perform_update(self, serializer):
        application = self.get_object()
        if not getattr(self.request.user, "is_company", False) or application.job.company_id != self.request.user.id:
            raise PermissionDenied("Only the hiring company can update this application.")

        old_status = application.status
        instance = serializer.save()

        if instance.status != old_status:
            ApplicationStatusHistory.objects.create(
                application=instance,
                old_status=old_status,
                new_status=instance.status,
                changed_by=self.request.user,
            )

    def perform_destroy(self, instance):
        if instance.applicant_id != self.request.user.id:
            raise PermissionDenied("You can only withdraw your own application.")
        if instance.status in (JobApplication.Status.ACCEPTED, JobApplication.Status.REJECTED):
            raise PermissionDenied("This application has already been finalized and cannot be withdrawn.")
        instance.delete()
