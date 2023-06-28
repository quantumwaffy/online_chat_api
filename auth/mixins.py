from starlette.requests import Request

from core.settings import SETTINGS

from . import utils


class JWTAuthMixin:
    def __init__(
        self,
        *,
        name: str = SETTINGS.AUTH.JWT_TOKEN_NAME,
        description: str = "JWT authentication token",
        scheme_name: str = "JWT",
        auto_error: bool = True,
    ) -> None:
        super().__init__(name=name, description=description, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
    ) -> str:
        token: str = await super().__call__(request)
        user_nickname: str = utils.Authenticator.get_user_nickname_from_token(
            token, SETTINGS.AUTH.JWT_ACCESS_TOKEN_SECRET_KEY
        )
        return user_nickname
