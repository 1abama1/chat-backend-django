from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Chat
from .serializers import ChatSerializer, ChatListSerializer

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatListSerializer
        return ChatSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        # Если private чат, проверяем существующий
        if request.data.get('type') == Chat.PRIVATE:
            members = request.data.get('members', [])
            if len(members) == 1:
                other_user_id = members[0]
                existing = Chat.objects.filter(
                    type=Chat.PRIVATE,
                    members=request.user
                ).filter(members=other_user_id).distinct().first()

                if existing:
                    serializer = self.get_serializer(existing)
                    return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        chat = serializer.save()
        chat.members.add(self.request.user)

