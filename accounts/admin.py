from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, JobSeekerProfile, CompanyProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = ("email", "username", "role", "is_verified", "is_staff", "is_active")
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("email", "username", "phone_number")

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "experience_years")
    search_fields = ("user__email", "first_name", "last_name", "skills")

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "industry", "founded_year")
    search_fields = ("company_name", "user__email", "industry")
