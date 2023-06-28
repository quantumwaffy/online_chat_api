from broadcaster import Broadcast

from .settings import SETTINGS


def get_broadcast() -> Broadcast:
    return Broadcast(SETTINGS.REDIS.url)


broadcast: Broadcast = get_broadcast()
