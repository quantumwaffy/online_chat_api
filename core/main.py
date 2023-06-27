from beanie import init_beanie
from broadcaster import Broadcast
from fastapi import FastAPI

from chat import schemas as chat_schemas

from . import routing
from .settings import SETTINGS


def get_broadcast() -> Broadcast:
    return Broadcast(SETTINGS.REDIS.url)


def get_app() -> FastAPI:
    api: FastAPI = FastAPI(
        debug=SETTINGS.APP.DEBUG,
        swagger_ui_parameters={"persistAuthorization": True},
        **{"docs_url": None, "redoc_url": None} if not SETTINGS.APP.DEBUG else {}
    )
    for prefix, routs in routing.AppRouter.routers:
        [api.include_router(router, prefix=prefix) for router in routs]
    return api


app: FastAPI = get_app()
broadcast: Broadcast = get_broadcast()


@app.on_event("startup")
async def startup() -> None:
    await broadcast.connect()
    await init_beanie(
        database=SETTINGS.MONGO.client[SETTINGS.MONGO.MONGO_INITDB_DATABASE],
        document_models=[chat_schemas.Message],
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    await broadcast.disconnect()
