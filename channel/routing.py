from django.urls import re_path, path

from .consumers import IndexConsumer, RoomConsumer, GameRoomConsumer

websocket_urlpatterns = [
    path("", IndexConsumer.as_asgi()),
    path("<str:room_pk>/", RoomConsumer.as_asgi()),
    path("<str:room_pk>/room", GameRoomConsumer.as_asgi()),
]
