from rest_framework import serializers
from .models import User, UserStatus

class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ['is_online', 'last_seen']

class UserSerializer(serializers.ModelSerializer):
    status = UserStatusSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'status']
        read_only_fields = ['id']

