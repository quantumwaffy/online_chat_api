import datetime
from json import JSONEncoder
from typing import Any


class DateTimeEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)
