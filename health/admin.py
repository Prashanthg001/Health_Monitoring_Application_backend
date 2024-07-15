from django.contrib import admin
from .models import ChatHistory

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_query', 'timestamp')
    search_fields = ('username', 'user_query')

admin.site.register(ChatHistory, ChatHistoryAdmin)