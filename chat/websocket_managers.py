import asyncio
import json

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from auth import models as auth_models
from core.broadcasting import broadcast

from . import json_codecs, models, schemas


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
                await self._websocket.send_json(json.loads(event.message))

    async def _receive(self) -> None:
        async for content in self._websocket.iter_text():
            if content:
                message_event: schemas.Message = schemas.Message(
                    content=content, nickname=self._user.nickname, chat_id=self._chat.id
                )
                await message_event.insert()
                await broadcast.publish(
                    self._chat.id,
                    message=schemas.MessageEvent(**message_event.dict()).json(
                        cls=json_codecs.DateTimeEncoder,
                    ),
                )

    async def run(self) -> None:
        try:
            await asyncio.wait(
                (asyncio.create_task(self._send()), asyncio.create_task(self._receive())),
                return_when=asyncio.FIRST_COMPLETED,
            )
        except WebSocketDisconnect:
            await self._websocket.close()
