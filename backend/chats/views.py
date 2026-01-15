from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.contrib.auth import get_user_model
from .models import Chat, ChatReadState
from .serializers import ChatCreateSerializer

User = get_user_model()


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        chats = Chat.objects.filter(members=request.user).distinct()
        return Response([chat.to_dict(user=request.user) for chat in chats])

    def create(self, request):
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data["type"] == Chat.PRIVATE:
            other = User.objects.filter(id=data["user_id"]).first()
            if not other:
                raise NotFound("User not found")

            existing = Chat.objects.filter(
                type=Chat.PRIVATE,
                members=request.user
            ).filter(members=other).distinct().first()

            if existing:
                return Response(existing.to_dict())

            chat = Chat.objects.create(type=Chat.PRIVATE)
            chat.members.add(request.user, other)
            
            ChatReadState.objects.get_or_create(chat=chat, user=request.user)
            ChatReadState.objects.get_or_create(chat=chat, user=other)
            
            return Response(chat.to_dict(), status=status.HTTP_201_CREATED)

        member_ids = data["member_ids"]
        members = User.objects.filter(id__in=member_ids)
        
        if members.count() < 1:
            return Response(
                {"error": "Group chat requires at least 1 other member"},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat = Chat.objects.create(
            type=Chat.GROUP,
            name=data["name"]
        )
        chat.members.add(request.user, *members)
        
        for user in chat.members.all():
            ChatReadState.objects.get_or_create(chat=chat, user=user)
        
        return Response(chat.to_dict(), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='read')
    def update_read_state(self, request, pk=None):
        chat = Chat.objects.filter(id=pk, members=request.user).first()
        if not chat:
            raise NotFound("Chat not found")

        last_read_message_id = request.data.get("last_read_message_id")
        if last_read_message_id is None:
            return Response(
                {"error": "last_read_message_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        read_state, created = ChatReadState.objects.get_or_create(
            chat=chat,
            user=request.user
        )
        read_state.last_read_message_id = last_read_message_id
        read_state.save()

        return Response({"status": "ok"})
