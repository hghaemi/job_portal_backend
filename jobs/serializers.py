from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import CompanyPublicSerializer
from accounts.models import CompanyProfile

from .models import JobCategory, JobPosting


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ("id", "name", "slug")


class JobPostingListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_profile.company_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    applications_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = JobPosting
        fields = (
            "id", "title", "company_name", "category_name", "location", "is_remote",
            "job_type", "experience_level", "salary_min", "salary_max", "salary_is_visible",
            "vacancies", "status", "application_deadline", "applications_count", "created_at",
        )


class JobPostingDetailSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    company_detail = CompanyPublicSerializer(source="company.company_profile", read_only=True)
    applications_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = JobPosting
        fields = (
            "id", "company", "company_detail", "category", "title", "description",
            "requirements", "responsibilities", "location", "is_remote", "job_type",
            "experience_level", "salary_min", "salary_max", "salary_is_visible",
            "vacancies", "status", "application_deadline", "applications_count",
            "created_at", "updated_at", "published_at",
        )
        read_only_fields = ("id", "company", "created_at", "updated_at", "published_at")

    def validate(self, attrs):
        salary_min = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_min": "salary_min cannot be greater than salary_max."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["company"] = request.user
        if validated_data.get("status") == JobPosting.Status.PUBLISHED:
            validated_data["published_at"] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        was_published = instance.status == JobPosting.Status.PUBLISHED
        instance = super().update(instance, validated_data)
        if instance.status == JobPosting.Status.PUBLISHED and not was_published:
            instance.published_at = timezone.now()
            instance.save(update_fields=["published_at"])
        return instance
