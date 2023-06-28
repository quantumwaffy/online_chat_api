import asyncio

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from auth import models as auth_models
from core.broadcasting import broadcast

from . import models, schemas


class BaseWebSocketManager:
    def __init__(
        self,
        websocket: WebSocket,
        user: auth_models.User,
        chat: models.Chat,
    ) -> None:
        self._websocket: WebSocket = websocket
        self._user: auth_models.User = user
        self._chat: models.Chat = chat

    async def _send(self) -> None:
        async with broadcast.subscribe(channel=self._chat.id) as subscriber:
            async for event in subscriber:
                await self._websocket.send_text(event.message)

    async def _save_message(self, content: str) -> None:
        await schemas.Message(content=content, chat_id=self._chat.id, nickname=self._user.nickname).insert()

    async def _receive(self) -> None:
        async for message_event in self._websocket.iter_text():
            if message_event:
                await self._save_message(message_event)
                await broadcast.publish(self._chat.id, message=message_event)

    async def run(self) -> None:
        try:
            await asyncio.wait(
                (asyncio.create_task(self._send()), asyncio.create_task(self._receive())),
                return_when=asyncio.FIRST_COMPLETED,
            )
        except WebSocketDisconnect:
            await self._websocket.close()
