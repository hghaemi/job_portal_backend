from django.conf import settings
from django.db import models

from jobs.models import JobPosting


def cover_letter_upload_path(instance, filename):
    return f"cover_letters/user_{instance.applicant_id}/{filename}"


class JobApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        ACCEPTED = "accepted", "Accepted"
        WITHDRAWN = "withdrawn", "Withdrawn"

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="applications", limit_choices_to={"role": "jobseeker"})

    cover_letter = models.TextField(blank=True)
    resume_snapshot = models.FileField(upload_to=cover_letter_upload_path, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    company_notes = models.TextField(
        blank=True, help_text="Internal notes visible only to the hiring company."
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["job", "applicant"], name="unique_job_application")
        ]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.applicant} -> {self.job} ({self.status})"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="status_history"
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.application_id}: {self.old_status} -> {self.new_status}"
