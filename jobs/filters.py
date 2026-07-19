import django_filters as filters

from .models import JobPosting


class JobPostingFilter(filters.FilterSet):
    keyword = filters.CharFilter(method="filter_keyword")
    location = filters.CharFilter(field_name="location", lookup_expr="icontains")
    category = filters.NumberFilter(field_name="category_id")
    job_type = filters.ChoiceFilter(choices=JobPosting.JobType.choices)
    experience_level = filters.ChoiceFilter(choices=JobPosting.ExperienceLevel.choices)
    is_remote = filters.BooleanFilter()
    salary_min = filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    class Meta:
        model = JobPosting
        fields = [
            "keyword", "location", "category", "job_type",
            "experience_level", "is_remote", "salary_min", "salary_max",
        ]

    def filter_keyword(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(title__icontains=value)
            | Q(description__icontains=value)
            | Q(requirements__icontains=value)
        )
