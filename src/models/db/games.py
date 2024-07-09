from typing import TYPE_CHECKING

from tortoise import fields

from src.models.db.base import BaseModel

if TYPE_CHECKING:
    from src.models.db.players import Player


class Game(BaseModel):
    name = fields.TextField()
    primary_game = fields.BooleanField(default=False)
    nickname = fields.TextField(default="")
    active = fields.BooleanField(default=True)
    turn = fields.IntField(default=0)
    time_left = fields.TextField(null=True)
    players: fields.ManyToManyRelation["Player"] = fields.ManyToManyField(
        model_name="models.Player", related_name="games", on_delete=fields.OnDelete.CASCADE
    )
