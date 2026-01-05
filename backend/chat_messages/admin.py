from django.contrib import admin
from .models import Message, MessageStatus, PinnedMessage

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'sender', 'text', 'created_at', 'is_deleted']
    list_filter = ['created_at', 'is_deleted', 'is_edited']

@admin.register(MessageStatus)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'delivered', 'read', 'delivered_at', 'read_at']

@admin.register(PinnedMessage)
class PinnedMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'message', 'pinned_by', 'pinned_at']

