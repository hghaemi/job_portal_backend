from django.contrib import admin

from .models import JobApplication, ApplicationStatusHistory


class StatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    readonly_fields = ("old_status", "new_status", "changed_by", "changed_at")
    can_delete = False


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "job", "status", "applied_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("applicant__email", "job__title")
    inlines = [StatusHistoryInline]
