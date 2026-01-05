from rest_framework import serializers
from .models import Message, MessageStatus, PinnedMessage

class MessageStatusSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MessageStatus
        fields = ['user', 'username', 'delivered', 'read', 'delivered_at', 'read_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    statuses = MessageStatusSerializer(many=True, read_only=True)
    forwarded_from_username = serializers.CharField(
        source='forwarded_from.sender.username',
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'chat',
            'sender',
            'sender_username',
            'text',
            'forwarded_from',
            'forwarded_from_username',
            'is_edited',
            'edited_at',
            'is_deleted',
            'created_at',
            'statuses'
        ]
        read_only_fields = ['sender', 'is_edited', 'edited_at', 'is_deleted']

class PinnedMessageSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)
    pinned_by_username = serializers.CharField(source='pinned_by.username', read_only=True)

    class Meta:
        model = PinnedMessage
        fields = ['id', 'chat', 'message', 'pinned_by', 'pinned_by_username', 'pinned_at']

