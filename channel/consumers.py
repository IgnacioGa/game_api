from user.serializers import CreateUserProfileSerializer
from .utils import UUIDEncoder
from .models import Room
import uuid

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from channels.layers import get_channel_layer


class RoomConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.room_id = self.scope['url_route']['kwargs']['room_pk']
        self.room = Room.objects.get(id=self.room_id)

        if self.user not in self.room.online.all():
            return

        self.accept()

        async_to_sync(self.channel_layer.group_add)(self.room_id, self.channel_name)

    def disconnect(self, code):
        self.room.online.remove(self.user)
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                "type": "user_leave",
                "message": "user leave the room",
                "user": CreateUserProfileSerializer(self.user).data
            },
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                "type": "list_of_users",
                "users": [CreateUserProfileSerializer(user).data for user in self.room.online.all()],
            },
        )
        async_to_sync(self.channel_layer.group_discard)(self.room_id, self.channel_name)
        return super().disconnect(code)

    def receive(self, text_data):
        json_data = json.loads(text_data)

        if json_data["type"] == 'create_room':

            async_to_sync(self.channel_layer.group_send)(
                self.room_id,
                {
                    "type": "room_created",
                    "message": "welcome to the room",
                },
            )

        if json_data["type"] == 'join_room':

            self.channel_layer = get_channel_layer()
            async_to_sync( self.channel_layer.group_send)(
                self.room_id,
                {
                    "type": "user_joined",
                    "message": "welcome to the room joined",
                },
            )

        if json_data["type"] == 'start_game':
            async_to_sync( self.channel_layer.group_send)(
                self.room_id,
                {
                    "type": "start_game",
                    "message": "welcome to the room joined",
                },
            )

        async_to_sync(self.channel_layer.group_send)(
            self.room_id,
            {
                "type": "list_of_users",
                "users": [CreateUserProfileSerializer(user).data for user in self.room.online.all()],
            },
        )

        return super().receive(text_data)
    
    def room_created(self, event):
        self.send(text_data=json.dumps({
            'type': 'room_created',
            "message": event['message'],
        }))

    def user_joined(self, event):
        self.send(text_data=json.dumps({
            'type': 'user_joined',
            "message": event['message'],
        }))

    def list_of_users(self, event):
        self.send(text_data=json.dumps({
            'type': 'list_of_users',
            "users": event['users'],
        }))

    def user_leave(self, event):
        self.send(text_data=json.dumps({
            'type': 'user_leave',
            "message": event['message'],
            "user": event['user']
        }))

    def start_game(self, event):
        self.send(text_data=json.dumps({
            'type': 'start_game',
        }))
        async_to_sync(self.channel_layer.group_discard)(self.room_id, self.channel_name)


class IndexConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room = None
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        json_data = json.loads(text_data)

        if json_data["type"] == 'create_room':
            
            self.room = Room.objects.create(owner=self.user)
            self.room_id = self.room.pk
            
            self.room.online.add(self.user)
            self.send(text_data=json.dumps({
                'type': 'create_room',
                "message": "Hey there! You've successfully connected!",
                "roomId": self.room_id
            }, cls=UUIDEncoder))

        if json_data["type"] == 'join_room':
            join_room_id = uuid.UUID(json_data["room_id"])

            try:
                self.room = Room.objects.get(id=join_room_id)
                self.room.online.add(self.user)
                self.send(text_data=json.dumps({
                    'type': 'join_room',
                    "message": "Welcome to the room",
                }))
                
            except:
                self.send(text_data=json.dumps({
                    'type': 'join_room_failed',
                    "message": "Room Not Found",
                }))

        return super().receive(text_data)


class GameRoomConsumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room = None
        self.user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.room_id = self.scope['url_route']['kwargs']['room_pk']
        self.room = Room.objects.get(id=self.room_id)

        if self.user not in self.room.online.all():
            return

        self.accept()

        async_to_sync(self.channel_layer.group_add)(self.room_id, self.channel_name)