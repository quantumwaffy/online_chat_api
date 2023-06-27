from fastapi import HTTPException, status


class BaseChatExceptionManager:
    not_subscribed: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="The user is not a member of this chat",
    )
    no_chat: HTTPException = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find chat",
    )
