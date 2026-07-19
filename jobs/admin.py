from django.contrib import admin

from .models import JobCategory, JobPosting


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "category", "job_type", "status",
                    "location", "vacancies", "application_deadline", "created_at",)     
    
    list_filter = ("status", "job_type", "experience_level", "is_remote", "category")
    search_fields = ("title", "description", "company__email", "location")
    autocomplete_fields = ("company", "category")
