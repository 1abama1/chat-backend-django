from django.contrib import admin
from .models import Chat, ChatReadState

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'name', 'created_at']
    filter_horizontal = ['members']

@admin.register(ChatReadState)
class ChatReadStateAdmin(admin.ModelAdmin):
    list_display = ['chat', 'user', 'last_read_message_id']

