from fastapi import FastAPI

from .settings import SETTINGS


def get_app() -> FastAPI:
    api: FastAPI = FastAPI(
        debug=SETTINGS.DEBUG,
        swagger_ui_parameters={"persistAuthorization": True},
        **{"docs_url": None, "redoc_url": None} if not SETTINGS.DEBUG else {}
    )
    return api


app: FastAPI = get_app()
