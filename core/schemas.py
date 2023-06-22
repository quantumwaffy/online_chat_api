from pydantic import BaseModel


class ResponseDetail(BaseModel):
    detail: str
