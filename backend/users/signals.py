from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserStatus

@receiver(post_save, sender=User)
def create_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.create(user=instance)

