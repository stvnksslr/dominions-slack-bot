from pydantic.main import BaseModel


class PlayerStatus(BaseModel):
    name: str
    turn_status: str
    turn_emoji: str | None = None

    def short_name(self):
        return self.name.split(",")[0].lower()
