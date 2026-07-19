from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):

    class Role(models.TextChoices):
        JOBSEEKER = "jobseeker", "Job Seeker"
        COMPANY = "company", "Company"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    phone_number = models.CharField(max_length=11, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_jobseeker(self):
        return self.role == self.Role.JOBSEEKER

    @property
    def is_company(self):
        return self.role == self.Role.COMPANY


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user_id}/{filename}"


def company_logo_upload_path(instance, filename):
    return f"company_logos/user_{instance.user_id}/{filename}"


class JobSeekerProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="jobseeker_profile")
    
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    education = models.TextField(blank=True) 
    skills = models.TextField(blank=True, help_text="Comma separated list of skills.")
    experience_years = models.PositiveSmallIntegerField(default=0)
    resume_file = models.FileField(upload_to=resume_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"JobSeekerProfile<{self.user.email}>"

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=150, blank=True)
    logo = models.ImageField(upload_to=company_logo_upload_path, null=True, blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CompanyProfile<{self.company_name}>"
