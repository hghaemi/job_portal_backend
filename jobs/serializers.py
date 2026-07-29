from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import CompanyPublicSerializer
from accounts.models import CompanyProfile

from .models import JobCategory, JobPosting


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ("id", "name", "slug")


def _is_owning_company(obj, request):
    user = getattr(request, "user", None)
    return bool(
        user
        and getattr(user, "is_company", False)
        and obj.company_id == user.id
    )


class JobPostingListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_profile.company_name", read_only=True)
    company_logo = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = (
            "id", "title", "company_name", "company_logo", "category_name", "location", "is_remote",
            "job_type", "experience_level", "salary_min", "salary_max", "salary_is_visible",
            "status", "application_deadline", "applications_count", "created_at",
        )

    def get_company_logo(self, obj):
        profile = getattr(obj.company, "company_profile", None)
        if profile and profile.logo:
            request = self.context.get("request")
            url = profile.logo.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_applications_count(self, obj):
        request = self.context.get("request")
        if _is_owning_company(obj, request):
            return getattr(obj, "applications_count", 0)
        return 0


class JobPostingDetailSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    company_detail = CompanyPublicSerializer(source="company.company_profile", read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = (
            "id", "company", "company_detail", "category", "title", "description",
            "requirements", "responsibilities", "location", "is_remote", "job_type",
            "experience_level", "salary_min", "salary_max", "salary_is_visible",
            "status", "application_deadline", "applications_count",
            "created_at", "updated_at", "published_at",
        )
        read_only_fields = ("id", "company", "created_at", "updated_at", "published_at")

    def get_applications_count(self, obj):
        request = self.context.get("request")
        if _is_owning_company(obj, request):
            return getattr(obj, "applications_count", 0)
        return 0

    def validate(self, attrs):
        is_remote = attrs.get("is_remote", getattr(self.instance, "is_remote", False))
        location = attrs.get("location", getattr(self.instance, "location", ""))
        salary_min = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_min": "salary_min cannot be greater than salary_max."}
            )
        if not is_remote and not location:
            raise serializers.ValidationError(
                {"location": "Location is required unless the job is remote."}
            )

        application_deadline = attrs.get("application_deadline")
        if self.instance is None and application_deadline and application_deadline < timezone.now().date():
            raise serializers.ValidationError(
                {"application_deadline": "Application deadline cannot be in the past."}
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