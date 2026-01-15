from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from django.utils import timezone
from chats.models import Chat
from .models import Message, MessageStatus, PinnedMessage
from .serializers import MessageSerializer, PinnedMessageSerializer


class ChatMessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, chat_id=None):
        chat = Chat.objects.filter(id=chat_id, members=request.user).first()
        if not chat:
            raise NotFound("Chat not found")

        messages = Message.objects.filter(
            chat=chat,
            is_deleted=False
        ).select_related('sender').order_by('created_at')

        return Response([m.to_dict() for m in messages])

    def create(self, request, chat_id=None):
        chat = Chat.objects.filter(id=chat_id, members=request.user).first()
        if not chat:
            raise NotFound("Chat not found")

        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=text
        )

        members = chat.members.exclude(id=request.user.id)
        for user in members:
            MessageStatus.objects.create(
                message=message,
                user=user,
                delivered=True,
                delivered_at=timezone.now()
            )

        return Response(message.to_dict(), status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            chat__members=self.request.user
        ).select_related('sender', 'chat')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.sender != request.user:
            raise PermissionDenied("You can only edit your own messages")

        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.text = text
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.save()

        return Response(instance.to_dict())

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.sender != request.user:
            raise PermissionDenied("You can only delete your own messages")

        instance.is_deleted = True
        instance.text = "Message deleted"
        instance.save(update_fields=['is_deleted', 'text'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', '')
        user = request.user

        qs = Message.objects.filter(
            chat__members=user,
            text__icontains=query,
            is_deleted=False
        ).select_related('sender', 'chat')[:50]

        return Response([m.to_dict() for m in qs])


class PinnedMessageViewSet(viewsets.ModelViewSet):
    serializer_class = PinnedMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat')
        if chat_id:
            return PinnedMessage.objects.filter(
                chat_id=chat_id,
                chat__members=self.request.user
            )
        return PinnedMessage.objects.filter(chat__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(pinned_by=self.request.user)
