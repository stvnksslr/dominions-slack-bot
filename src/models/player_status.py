from pydantic.main import BaseModel


class PlayerStatus(BaseModel):
    name: str
    turn_status: str

