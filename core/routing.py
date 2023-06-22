import dataclasses

from fastapi import APIRouter

from auth.routers import auth_router, register_router


@dataclasses.dataclass
class AppRouter:
    v1: tuple[APIRouter, ...] = (
        auth_router,
        register_router,
    )

    @classmethod
    @property
    def routers(cls) -> tuple[tuple[str, tuple[APIRouter, ...]], ...]:
        return tuple(
            [
                (f"/api/{f_name}", f_obj.default)
                for f_name, f_obj in cls.__dataclass_fields__.items()
                if not f_name.startswith("_")
            ]
        )
