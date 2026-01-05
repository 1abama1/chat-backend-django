from rest_framework import serializers
from .models import Chat
from users.models import User
from chat_messages.models import Message

class ChatSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )

    class Meta:
        model = Chat
        fields = ['id', 'type', 'name', 'members', 'created_at']

class ChatListSerializer(ChatSerializer):
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta(ChatSerializer.Meta):
        fields = ChatSerializer.Meta.fields + ['unread_count', 'last_message']

    def get_unread_count(self, chat):
        user = self.context['request'].user
        state = chat.read_states.filter(user=user).first()
        last_read = state.last_read_message_id if state else 0

        return Message.objects.filter(
            chat=chat,
            id__gt=last_read
        ).exclude(sender=user).count()

    def get_last_message(self, chat):
        msg = chat.messages.order_by('-id').first()
        return {
            'id': msg.id,
            'text': msg.text,
            'sender': msg.sender.username,
            'created_at': msg.created_at
        } if msg else None

