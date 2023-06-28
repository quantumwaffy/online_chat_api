from fastapi import APIRouter, HTTPException, WebSocket, status
from starlette.responses import HTMLResponse

from auth import dependencies as auth_deps
from auth import models as auth_models
from auth import schemas as auth_schemas
from auth import utils as auth_utils
from core import dependencies as core_deps
from core import schemas as core_schemas

from . import models, schemas, utils, websocket_managers

chat_router: APIRouter = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={401: {"model": core_schemas.ResponseDetail}},
)


@chat_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: schemas.ChatInput,
    sql_session: core_deps.SqlSession,
    user: auth_deps.UserHeader,
) -> schemas.ChatDB:
    chat: models.Chat = await models.Chat(**chat_data.dict()).create(sql_session)
    user.chats.append(chat)
    await sql_session.commit()
    return schemas.ChatDB.from_orm(chat)


@chat_router.get("/{chat_id}")
async def get_chat_history(
    chat_id: str,
    sql_session: core_deps.SqlSession,
    user: auth_deps.UserHeader,
    skip: int,
    limit: int = 50,
) -> schemas.ChatHistory:
    return await utils.ChatHistoryMaker(user, chat_id, sql_session, skip, limit).get()


@chat_router.post("/add-user-to-chat")
async def add_user_to_chat(
    data: schemas.UserToChat,
    sql_session: core_deps.SqlSession,
    user: auth_deps.UserHeader,
) -> auth_schemas.UserDB:
    chat: models.Chat = await utils.ChatGetter(user, data.chat_id, sql_session).get()
    user_for_chat: auth_models.User = await auth_utils.Authenticator(sql_session).get_prefetched_user(
        data.user_nickname
    )
    user_for_chat.chats.append(chat)
    await sql_session.commit()
    await sql_session.refresh(user_for_chat, attribute_names=("chats",))
    return auth_schemas.UserDB.from_orm(user_for_chat)


@chat_router.websocket("/ws/{chat_id}/{token}")
async def websocket_manager(
    websocket: WebSocket,
    sql_session: core_deps.SqlSession,
    chat_id: str,
    token: str,
):
    await websocket.accept()
    try:
        user: auth_models.User = await auth_utils.Authenticator(sql_session).get_prefetched_user_from_token(token)
        chat: models.Chat = await utils.ChatGetter(user, chat_id, sql_session).get()
    except HTTPException as e:
        await websocket.send_text(e.detail)
        await websocket.close()
    else:
        await websocket_managers.BaseWebSocketManager(websocket, user, chat).run()


# TODO: REMOVE CODE BELOW - ONLY FOR TEST
@chat_router.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
   <head>
      <title>Chat</title>
         <script>
   var ws = new WebSocket(
   "ws://127.0.0.1:8000/api/v1/chat/ws/de06a3eb-ba12-43a1-a751-6c08f7746b9e/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXV\
CJ9.eyJzdWIiOiJxd2VydHkiLCJleHAiOjE3NDc4NTk2OTZ9.KdlnT2fRHy-6ZPmpcMRhlsnWzeBJ2ifYuO4JuBl9EBg");
   ws.onmessage = function(event) {
   var messages = document.getElementById('messages')
   var message = document.createElement('li')
   var content = document.createTextNode(event.data)
   message.appendChild(content)
   messages.appendChild(message)
};
function sendMessage(event) {
   var input = document.getElementById("messageText")
   ws.send(input.value)
   input.value = ''
   event.preventDefault()
}
   </script>
   </head>
   <body>
      <h1>WebSocket Chat</h1>
      <form action="" onsubmit="sendMessage(event)">
      <input type="text" id="messageText" autocomplete="off"/>
      <button>Send</button>
      </form>
      <ul id='messages'>
      </ul>
   </body>
</html>
   """
    )
