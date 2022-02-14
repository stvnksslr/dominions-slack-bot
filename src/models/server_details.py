from pydantic import BaseModel


class ServerDetails(BaseModel):
    name: str
    turn: str
    hours_remaining: str
