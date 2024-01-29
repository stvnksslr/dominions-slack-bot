from pydantic.main import BaseModel

from src.models.player_status import PlayerStatus


class LobbyDetails(BaseModel):
    server_info: str
    player_status: list[PlayerStatus]
