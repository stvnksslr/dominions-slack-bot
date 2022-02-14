from pydantic import BaseModel, Field

from src.models.snek_server_status import NationType, TurnStatus


class Nation(BaseModel):
    """
    Nation Object Representing either a human player, ai or defeated nation
    """
    game_id: str = Field(alias="id")
    name: str
    epithet: str
    pretender_id: str
    controller: NationType
    ai_level: str
    turn_played: TurnStatus
    filename: str
