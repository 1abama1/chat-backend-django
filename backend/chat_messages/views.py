from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Message, MessageStatus, PinnedMessage
from .serializers import MessageSerializer, PinnedMessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat')
        if chat_id:
            return Message.objects.filter(
                chat_id=chat_id,
                chat__members=self.request.user,
                is_deleted=False
            ).select_related('sender', 'chat').prefetch_related('statuses').order_by('-created_at')
        return Message.objects.none()

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        
        # Создаем статусы delivered для всех участников кроме отправителя
        members = message.chat.members.exclude(id=self.request.user.id)
        for user in members:
            MessageStatus.objects.create(
                message=message,
                user=user,
                delivered=True,
                delivered_at=timezone.now()
            )

    def perform_update(self, serializer):
        serializer.save(
            is_edited=True,
            edited_at=timezone.now()
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.text = 'Message deleted'
        instance.save(update_fields=['is_deleted', 'text'])

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', '')
        user = request.user

        qs = Message.objects.filter(
            chat__members=user,
            text__icontains=query,
            is_deleted=False
        ).select_related('sender', 'chat')[:50]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class PinnedMessageViewSet(viewsets.ModelViewSet):
    serializer_class = PinnedMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat')
        if chat_id:
            return PinnedMessage.objects.filter(chat_id=chat_id, chat__members=self.request.user)
        return PinnedMessage.objects.filter(chat__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(pinned_by=self.request.user)

