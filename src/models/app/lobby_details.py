from pydantic.main import BaseModel

from .player_status import PlayerStatus


class LobbyDetails(BaseModel):
    server_info: str
    player_status: list[PlayerStatus]
    turn: str
    time_left: str | None = None
