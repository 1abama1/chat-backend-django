from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat

User = get_user_model()


class ChatCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[("private", "Private"), ("group", "Group")])
    user_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    def validate(self, data):
        chat_type = data["type"]

        if chat_type == Chat.Type.PRIVATE:
            if "user_id" not in data:
                raise serializers.ValidationError(
                    {"user_id": "Required for private chat"}
                )

        if chat_type == Chat.Type.GROUP:
            if not data.get("name"):
                raise serializers.ValidationError(
                    {"name": "Required for group chat"}
                )
            if not data.get("member_ids"):
                raise serializers.ValidationError(
                    {"member_ids": "Required for group chat"}
                )

        return data
