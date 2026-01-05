from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="status")
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def go_online(self):
        self.is_online = True
        self.save(update_fields=["is_online"])

    def go_offline(self):
        self.is_online = False
        self.last_seen = timezone.now()
        self.save(update_fields=["is_online", "last_seen"])

