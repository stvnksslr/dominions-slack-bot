from pydantic import BaseModel


class ServerDetails(BaseModel):
    """
    Hours remaining in a turn and current turn are not tracked by snek.earth or are broken and must be pulled from the game
    server itself
    """
    name: str
    turn: str
    hours_remaining: str
