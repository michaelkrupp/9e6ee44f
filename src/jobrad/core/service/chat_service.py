import asyncio
from asyncio import gather
from typing import Final
from uuid import uuid4

from fastapi import WebSocket

from ...domain.chat_message import ChatMessage
from ...domain.chat_notification import (
    ChatNotification,
    ChatNotificationKind,
)
from ...domain.chat_room import ChatRoom, ChatRoomID
from ...infrastructure.logging import get_logger

logger: Final = get_logger(__name__)


class ChatService:
    _rooms: dict[ChatRoomID, ChatRoom]
    _rooms_lock: asyncio.Lock

    _room_messages: dict[ChatRoomID, list[ChatMessage]]
    _room_clients: dict[ChatRoomID, set[WebSocket]]
    _room_lock: dict[ChatRoomID, asyncio.Lock]

    _notification_clients: set[WebSocket]
    _notification_lock: asyncio.Lock

    def __init__(self):
        self._rooms = {}
        self._rooms_lock = asyncio.Lock()
        self._room_messages = {}
        self._room_clients = {}
        self._room_lock = {}
        self._notification_clients = set()
        self._notification_lock = asyncio.Lock()

    async def create_chat_room(self) -> ChatRoom:
        chat_room = ChatRoom(id=str(uuid4()))

        self._rooms[chat_room.id] = chat_room
        self._room_messages[chat_room.id] = []
        self._room_clients[chat_room.id] = set()
        self._room_lock[chat_room.id] = asyncio.Lock()

        logger.info(f"Chat room created", chat_room_id=chat_room.id)

        await self.send_notification(
            ChatNotification(
                kind=ChatNotificationKind.ROOMS_UPDATED,
                room_ids=list(self._rooms.keys()),
                id=str(uuid4()),
            )
        )

        return chat_room

    async def get_chat_room(self, chat_room_id: ChatRoomID) -> ChatRoom:
        return self._rooms[chat_room_id]

    async def get_chat_rooms(self) -> list[ChatRoom]:
        async with self._rooms_lock:
            return list(self._rooms.values())

    async def subscribe_messages(self, chat_room_id: ChatRoomID, ws: WebSocket):
        # add client and send history
        async with self._room_lock[chat_room_id]:
            self._room_clients[chat_room_id].add(ws)
            for message in self._room_messages[chat_room_id]:
                await ws.send_text(message.to_json())

        logger.info(
            "Client added to chat room",
            client_id=id(ws),
            chat_room_id=chat_room_id,
        )

    async def subscribe_notifications(self, ws: WebSocket):
        async with self._notification_lock:
            self._notification_clients.add(ws)
        async with self._rooms_lock:
            await ws.send_text(
                ChatNotification(
                    kind=ChatNotificationKind.ROOMS_UPDATED,
                    room_ids=list(self._rooms.keys()),
                    id=str(uuid4()),
                ).to_json()
            )

    async def unsubscribe_messages(self, chat_room_id: ChatRoomID, ws: WebSocket):
        async with self._room_lock[chat_room_id]:
            self._room_clients[chat_room_id].remove(ws)

        logger.info(
            "Client removed from chat room",
            client_id=id(ws),
            chat_room_id=chat_room_id,
        )

        await self._try_prune_chat_room(chat_room_id)

    async def _try_prune_chat_room(self, chat_room_id: ChatRoomID):
        async with self._room_lock[chat_room_id]:
            clients = self._room_clients[chat_room_id] - self._notification_clients
            if len(clients) > 0:
                return
            self._rooms.pop(chat_room_id)
            self._room_messages.pop(chat_room_id)
            self._room_clients.pop(chat_room_id)
            self._room_lock.pop(chat_room_id)

        logger.info("Chat room pruned", chat_room_id=chat_room_id)

        await self.send_notification(
            ChatNotification(
                kind=ChatNotificationKind.ROOMS_UPDATED,
                room_ids=list(self._rooms.keys()),
                id=str(uuid4()),
            )
        )

    async def unsubscribe_notifications(self, ws: WebSocket):
        async with self._notification_lock:
            self._notification_clients.remove(ws)

    async def send_message(self, chat_room_id: ChatRoomID, chat_message: ChatMessage):
        async with self._room_lock[chat_room_id]:
            self._room_messages[chat_room_id].append(chat_message)

            gather(
                *(
                    ws.send_text(chat_message.to_json())
                    for ws in self._room_clients[chat_room_id]
                )
            )

    async def send_notification(self, chat_notification: ChatNotification):
        async with self._notification_lock:
            gather(
                *(
                    ws.send_text(chat_notification.to_json())
                    for ws in self._notification_clients
                )
            )
