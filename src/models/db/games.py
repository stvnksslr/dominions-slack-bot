from typing import TYPE_CHECKING

from tortoise import fields

from src.models.db.base import BaseModel

if TYPE_CHECKING:
    from src.models.db.players import Player


class Game(BaseModel):
    name = fields.TextField()
    nickname = fields.TextField()
    active = fields.BooleanField()
    turn = fields.IntField()
    players: fields.ManyToManyRelation["Player"] = fields.ManyToManyField(
        "models.Player", related_name="games", through="game_player"
    )
