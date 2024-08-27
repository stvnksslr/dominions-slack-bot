from typing import List

from pydantic.main import BaseModel


class PlayerStatus(BaseModel):
    name: str
    turn_status: str
    turn_emoji: str | None = None

    def short_name(self) -> str:
        return self.name.split(sep=",")[0].lower().strip()


class GameDetails(BaseModel):
    turn: int
    time_left: str
    player_status: List[PlayerStatus]
