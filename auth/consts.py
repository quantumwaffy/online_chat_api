from enum import StrEnum

PASSWORD_REGEX: str = r"^[A-Za-z0-9\№\,\;\'\-\.\"\)\(\+\&\*\@\:\!\/\?\=\%\$\#\!\|\}\{\[\]\^\~\`\\]+$"
NICKNAME_REGEX: str = r"^[a-zA-Z0-9.]+$"
NAME_REGEX: str = r"^[a-zA-Z]+$"


class CheckStatus(StrEnum):
    OK = "OK"
    FAIL = "FAIL"
