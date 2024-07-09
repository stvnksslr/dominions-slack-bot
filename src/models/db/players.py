from tortoise import fields

from src.models.db import Game
from src.models.db.base import BaseModel


class Player(BaseModel):
    nation = fields.TextField(null=False)
    short_name = fields.TextField(null=False)
    player_name = fields.TextField(null=True)
    turn_status = fields.TextField(default="Turn unfinished")
    game: fields.ForeignKeyRelation[Game] = fields.ForeignKeyField(model_name="models.Game", related_name="games")

    def __str__(self) -> str:
        return self.nation.split(sep=",")[0]
