import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user = self.scope["user"]

        if not self.user:
            await self.close()
            return

        is_member = await self.check_membership()
        if not is_member:
            await self.close()
            return

        self.room_group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.set_online()
        await self.notify_status(True)

    async def disconnect(self, code):
        await self.set_offline()
        await self.notify_status(False)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "message":
            msg = await self.save_message(data.get("text", ""))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": msg.id,
                    "text": msg.text,
                    "sender": self.user.username,
                    "sender_id": self.user.id,
                    "created_at": msg.created_at.isoformat(),
                }
            )

        elif data["type"] == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", True),
                }
            )

        elif data["type"] == "read":
            await self.update_read_state(data.get("last_read_message_id", 0))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "read_update",
                    "user_id": self.user.id,
                    "last_read_message_id": data.get("last_read_message_id", 0),
                }
            )

        elif data["type"] == "forward":
            msg = await self.forward_message(
                data.get("message_id"),
                data.get("target_chat_id")
            )
            if msg:
                await self.channel_layer.group_send(
                    f"chat_{data['target_chat_id']}",
                    {
                        "type": "chat_message",
                        "message_id": msg.id,
                        "text": msg.text,
                        "sender": self.user.username,
                        "sender_id": self.user.id,
                        "forwarded": True,
                        "forwarded_from": msg.forwarded_from.sender.username if msg.forwarded_from else None,
                        "created_at": msg.created_at.isoformat(),
                    }
                )

        elif data["type"] == "edit":
            await self.edit_message(data.get("message_id"), data.get("text"))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_edit",
                    "message_id": data.get("message_id"),
                    "text": data.get("text"),
                }
            )

        elif data["type"] == "delete":
            await self.delete_message(data.get("message_id"))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_delete",
                    "message_id": data.get("message_id"),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message_id": event["message_id"],
            "text": event["text"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "forwarded": event.get("forwarded", False),
            "forwarded_from": event.get("forwarded_from"),
            "created_at": event["created_at"],
        }))

    async def typing_event(self, event):
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "typing",
                "user_id": event["user_id"],
                "username": event["username"],
                "is_typing": event["is_typing"],
            }))

    async def read_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "read",
            "user_id": event["user_id"],
            "last_read_message_id": event["last_read_message_id"],
        }))

    async def message_edit(self, event):
        await self.send(text_data=json.dumps({
            "type": "message_edit",
            "message_id": event["message_id"],
            "text": event["text"],
        }))

    async def message_delete(self, event):
        await self.send(text_data=json.dumps({
            "type": "message_delete",
            "message_id": event["message_id"],
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        }))

    @database_sync_to_async
    def check_membership(self):
        from chats.models import Chat
        return Chat.objects.filter(id=self.chat_id, members=self.user).exists()

    @database_sync_to_async
    def save_message(self, text):
        from .models import Message, MessageStatus
        message = Message.objects.create(
            chat_id=self.chat_id,
            sender=self.user,
            text=text
        )

        members = message.chat.members.exclude(id=self.user.id)
        for user in members:
            MessageStatus.objects.create(
                message=message,
                user=user,
                delivered=True,
                delivered_at=timezone.now()
            )

        return message

    @database_sync_to_async
    def update_read_state(self, last_id):
        from chats.models import ChatReadState
        from .models import MessageStatus
        if last_id <= 0:
            return

        state, _ = ChatReadState.objects.get_or_create(
            chat_id=self.chat_id,
            user=self.user
        )

        if last_id > state.last_read_message_id:
            state.last_read_message_id = last_id
            state.save(update_fields=['last_read_message_id'])

            MessageStatus.objects.filter(
                message__chat_id=self.chat_id,
                message_id__lte=last_id,
                user=self.user,
                read=False
            ).update(
                read=True,
                read_at=timezone.now()
            )

    @database_sync_to_async
    def forward_message(self, message_id, target_chat_id):
        from .models import Message
        try:
            original = Message.objects.get(id=message_id)
            return Message.objects.create(
                chat_id=target_chat_id,
                sender=self.user,
                text=original.text,
                forwarded_from=original,
                forwarded_by=self.user
            )
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def edit_message(self, message_id, text):
        from .models import Message
        Message.objects.filter(
            id=message_id,
            sender=self.user
        ).update(
            text=text,
            is_edited=True,
            edited_at=timezone.now()
        )

    @database_sync_to_async
    def delete_message(self, message_id):
        from .models import Message
        Message.objects.filter(
            id=message_id,
            sender=self.user
        ).update(
            is_deleted=True,
            text='Message deleted'
        )

    @database_sync_to_async
    def set_online(self):
        from users.models import UserStatus
        status, _ = UserStatus.objects.get_or_create(user=self.user)
        status.go_online()

    @database_sync_to_async
    def set_offline(self):
        from users.models import UserStatus
        status, _ = UserStatus.objects.get_or_create(user=self.user)
        status.go_offline()

    @database_sync_to_async
    def get_user_chat_ids(self):
        from chats.models import Chat
        return list(
            Chat.objects.filter(members=self.user).values_list('id', flat=True)
        )

    async def notify_status(self, is_online):
        chat_ids = await self.get_user_chat_ids()

        for chat_id in chat_ids:
            await self.channel_layer.group_send(
                f"chat_{chat_id}",
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "is_online": is_online
                }
            )

