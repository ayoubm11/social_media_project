import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import Conversation, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # Announce presence to the group
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat.broadcast',
                'payload': {
                    'event': 'presence',
                    'user': user.username,
                    'status': 'online'
                }
            })

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # Announce offline presence
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat.broadcast',
                'payload': {
                    'event': 'presence',
                    'user': user.username,
                    'status': 'offline'
                }
            })

    async def receive_json(self, content, **kwargs):
        """Handle incoming JSON messages with different actions:
        - action: 'send' -> create Message and broadcast 'new_message' (includes temp_id if provided)
        - action: 'delivered' -> mark message delivered and broadcast 'delivered'
        - action: 'read' -> mark message read and broadcast 'read'
        """
        print(f"[DEBUG] receive_json: {content}")  # Debugging
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            print(f"[DEBUG] User not authenticated")
            return

        action = content.get('action')
        print(f"[DEBUG] action: {action}")

        if action == 'send':
            message_text = content.get('message', '').strip()
            temp_id = content.get('temp_id')
            print(f"[DEBUG] send: message_text={message_text}, temp_id={temp_id}")
            if not message_text:
                return
            message = await database_sync_to_async(self._save_message)(user, message_text)
            print(f"[DEBUG] Message saved: {message.id}")

            payload = {
                'event': 'new_message',
                'message': {
                    'id': message.id,
                    'sender': user.username,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                    'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
                    'read_at': message.read_at.isoformat() if message.read_at else None,
                }
            }
            if temp_id:
                payload['temp_id'] = temp_id

            print(f"[DEBUG] Sending payload: {payload}")
            await self.channel_layer.group_send(self.group_name, {'type': 'chat.broadcast', 'payload': payload})

        elif action == 'delivered':
            message_id = content.get('message_id')
            print(f"[DEBUG] delivered: message_id={message_id}")
            if not message_id:
                return
            msg = await database_sync_to_async(self._mark_delivered)(message_id)
            if msg:
                payload = {
                    'event': 'delivered',
                    'message': {'id': msg.id, 'delivered_at': msg.delivered_at.isoformat()}
                }
                await self.channel_layer.group_send(self.group_name, {'type': 'chat.broadcast', 'payload': payload})

        elif action == 'read':
            message_id = content.get('message_id')
            print(f"[DEBUG] read: message_id={message_id}")
            if not message_id:
                return
            msg = await database_sync_to_async(self._mark_read)(message_id)
            if msg:
                payload = {
                    'event': 'read',
                    'message': {'id': msg.id, 'read_at': msg.read_at.isoformat()}
                }
                await self.channel_layer.group_send(self.group_name, {'type': 'chat.broadcast', 'payload': payload})

    async def chat_broadcast(self, event):
        # Send payload JSON to WebSocket
        await self.send_json(event['payload'])

    def _save_message(self, user, text):
        conv = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(conversation=conv, sender=user, content=text, created_at=timezone.now())

    def _mark_delivered(self, message_id):
        try:
            m = Message.objects.get(id=message_id)
            if not m.delivered_at:
                m.delivered_at = timezone.now()
                m.save()
            return m
        except Message.DoesNotExist:
            return None

    def _mark_read(self, message_id):
        try:
            m = Message.objects.get(id=message_id)
            if not m.read_at:
                m.read_at = timezone.now()
                m.save()
            return m
        except Message.DoesNotExist:
            return None
