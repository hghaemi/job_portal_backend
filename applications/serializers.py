from rest_framework import serializers

from jobs.models import JobPosting
from jobs.serializers import JobPostingListSerializer
from accounts.serializers import JobSeekerProfileSerializer

from .models import JobApplication, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatusHistory
        fields = ("id", "old_status", "new_status", "changed_by", "changed_at")


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ("id", "job", "cover_letter", "resume_snapshot")
        read_only_fields = ("id",)

    def validate_job(self, job):
        if job.status != JobPosting.Status.PUBLISHED:
            raise serializers.ValidationError("This job posting is not open for applications.")
        return job

    def validate(self, attrs):
        request = self.context["request"]
        job = attrs.get("job") or getattr(self.instance, "job", None)
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        return attrs

    def create(self, validated_data):
        validated_data["applicant"] = self.context["request"].user
        return super().create(validated_data)


class JobApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(
        source="job.company.company_profile.company_name", read_only=True
    )

    class Meta:
        model = JobApplication
        fields = (
            "id", "job", "job_title", "company_name", "status",
            "applied_at", "updated_at",
        )


class JobApplicationDetailSerializer(serializers.ModelSerializer):
    job = JobPostingListSerializer(read_only=True)
    applicant_profile = JobSeekerProfileSerializer(source="applicant.jobseeker_profile", read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = JobApplication
        fields = (
            "id", "job", "applicant", "applicant_profile", "cover_letter",
            "resume_snapshot", "status", "company_notes", "status_history",
            "applied_at", "updated_at",
        )
        read_only_fields = (
            "id", "job", "applicant", "applicant_profile", "cover_letter",
            "resume_snapshot", "status_history", "applied_at", "updated_at",
        )


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ("status", "company_notes")

    def validate_status(self, value):
        allowed = dict(JobApplication.Status.choices)
        if value not in allowed:
            raise serializers.ValidationError("Invalid status.")
        return value
