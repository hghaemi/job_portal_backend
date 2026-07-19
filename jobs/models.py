from django.conf import settings
from django.db import models


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        REMOTE = "remote", "Remote"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", "Entry level"
        MID = "mid", "Mid level"
        SENIOR = "senior", "Senior level"
        MANAGER = "manager", "Manager"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_postings",
        limit_choices_to={"role": "company"},
    )
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)

    location = models.CharField(max_length=150)
    is_remote = models.BooleanField(default=False)

    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.ENTRY
    )

    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_is_visible = models.BooleanField(default=True)

    vacancies = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    application_deadline = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "job_type"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company.username}"

    @property
    def is_open(self):
        return self.status == self.Status.PUBLISHED