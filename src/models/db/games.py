from tortoise import fields

from src.models.db.base import BaseModel


class Game(BaseModel):
    name = fields.TextField()
    primary_game = fields.BooleanField(default=False)
    nickname = fields.TextField(default="")
    active = fields.BooleanField(default=True)
    turn = fields.IntField(default=0)
    time_left = fields.TextField(null=True)
