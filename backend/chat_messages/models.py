from django.db import models
from django.utils import timezone
from users.models import User
from chats.models import Chat

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    forwarded_from = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="forwards"
    )
    forwarded_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="forwarded_messages"
    )

    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"

    def to_dict(self):
        text = "Message deleted" if self.is_deleted else self.text
        
        return {
            "id": self.id,
            "sender": {
                "id": self.sender.id,
                "username": self.sender.username,
            },
            "text": text,
            "is_edited": self.is_edited,
            "created_at": self.created_at.isoformat(),
        }

class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="statuses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivered = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"Status for {self.user.username} - Message {self.message.id}"

class PinnedMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="pinned_messages")
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    pinned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    pinned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pinned: {self.message}"
