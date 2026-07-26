from tortoise import fields
from tortoise.fields import ForeignKeyRelation

from src.models.db.base import BaseModel
from src.models.db.games import Game


class Player(BaseModel):
    nation = fields.TextField(null=False)
    short_name = fields.TextField(null=False)
    player_name = fields.TextField(null=True)
    turn_status = fields.TextField(default="Turn unfinished")
    game: ForeignKeyRelation[Game] = fields.ForeignKeyField("models.Game", related_name="players")

    def __str__(self) -> str:
        return self.nation.split(sep=",")[0]
