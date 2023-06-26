from core import mixins as core_mixins


class ChatInput(core_mixins.ORMBaseModelMixin):
    name: str


class ChatDB(ChatInput):
    id: str
