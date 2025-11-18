from django.contrib import admin
from .models import Follow, Notification, Conversation, Message


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
	list_display = ('follower', 'following', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ('id', 'created_at')
	filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('id', 'conversation', 'sender', 'created_at')
	search_fields = ('sender__username', 'content')
