from django.contrib import admin
from .models import Service, ChatSession, ChatMessage, Agency


admin.site.register(Service)
admin.site.register(ChatMessage)
admin.site.register(ChatSession)
admin.site.register(Agency)
