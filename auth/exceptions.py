from fastapi import HTTPException, status


class BaseAuthExceptionManager:
    credentials_error: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    authentication_error: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    signup_user_exists: HTTPException = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User with this nickname already exists",
    )

    no_user: HTTPException = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find user",
    )

    blocked_user: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User was blocked",
    )

    token_expired: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
