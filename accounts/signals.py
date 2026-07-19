from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, JobSeekerProfile, CompanyProfile


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created, **kwargs):
    if not created:
        return

    if instance.role == User.Role.JOBSEEKER:
        JobSeekerProfile.objects.get_or_create(user=instance)
    elif instance.role == User.Role.COMPANY:
        CompanyProfile.objects.get_or_create(
            user=instance, defaults={"company_name": instance.username}
        )
