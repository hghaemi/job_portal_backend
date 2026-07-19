from django.db.models import Count, Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import JobPosting
from applications.models import JobApplication

from .permissions import IsCompany, IsJobSeeker


class CompanyDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get(self, request):
        company = request.user
        postings = JobPosting.objects.filter(company=company)

        postings_by_status = postings.values("status").annotate(count=Count("id"))
        applications = JobApplication.objects.filter(job__company=company)
        applications_by_status = applications.values("status").annotate(count=Count("id"))

        top_postings = (
            postings.annotate(applications_count=Count("applications"))
            .order_by("-applications_count")
            .values("id", "title", "applications_count")[:5]
        )

        return Response({
            "total_postings": postings.count(),
            "postings_by_status": {row["status"]: row["count"] for row in postings_by_status},
            "total_applications_received": applications.count(),
            "applications_by_status": {row["status"]: row["count"] for row in applications_by_status},
            "top_postings_by_applications": list(top_postings),
        })


class JobSeekerDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def get(self, request):
        user = request.user
        applications = JobApplication.objects.filter(applicant=user)
        applications_by_status = applications.values("status").annotate(count=Count("id"))

        recent = applications.select_related("job").order_by("-applied_at")[:5].values(
            "id", "job__title", "status", "applied_at"
        )

        return Response({
            "total_applications": applications.count(),
            "applications_by_status": {row["status"]: row["count"] for row in applications_by_status},
            "recent_applications": list(recent),
        })


class PlatformOverviewStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from accounts.models import User

        return Response({
            "open_jobs": JobPosting.objects.filter(status=JobPosting.Status.PUBLISHED).count(),
            "total_companies": User.objects.filter(role=User.Role.COMPANY).count(),
            "total_jobseekers": User.objects.filter(role=User.Role.JOBSEEKER).count(),
        })
