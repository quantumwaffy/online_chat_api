from core import mixins as core_mixins


class ChatDB(core_mixins.EnvSettingsMixin):
    id: int
    name: str
