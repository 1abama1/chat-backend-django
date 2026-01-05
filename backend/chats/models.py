from django.db import models
from users.models import User

class Chat(models.Model):
    PRIVATE = "private"
    GROUP = "group"

    CHAT_TYPES = [
        (PRIVATE, "Private"),
        (GROUP, "Group"),
    ]

    type = models.CharField(max_length=10, choices=CHAT_TYPES)
    name = models.CharField(max_length=255, null=True, blank=True)
    members = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_private(self):
        return self.type == self.PRIVATE

    def __str__(self):
        return self.name or f"Chat {self.id}"

class ChatReadState(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="read_states")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_read_message_id = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self):
        return f"{self.user.username} - Chat {self.chat.id}"

