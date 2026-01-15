from django.db import models
from users.models import User

class Chat(models.Model):
    class Type(models.TextChoices):
        PRIVATE = "private", "Private"
        GROUP = "group", "Group"

    PRIVATE = Type.PRIVATE
    GROUP = Type.GROUP

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

    def to_dict(self, user=None):
        from chat_messages.models import Message
        
        data = {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "members": [
                {"id": m.id, "username": m.username}
                for m in self.members.all()
            ],
        }
        
        if user:
            state = self.read_states.filter(user=user).first()
            last_read = state.last_read_message_id if state else 0
            
            unread_count = Message.objects.filter(
                chat=self,
                id__gt=last_read
            ).exclude(sender=user).count()
            
            last_msg = self.messages.order_by('-id').first()
            last_message = None
            if last_msg:
                last_message = {
                    "id": last_msg.id,
                    "text": last_msg.text,
                    "created_at": last_msg.created_at.isoformat(),
                }
            
            data["unread_count"] = unread_count
            data["last_message"] = last_message
        
        return data

class ChatReadState(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="read_states")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_read_message_id = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self):
        return f"{self.user.username} - Chat {self.chat.id}"

