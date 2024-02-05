from tortoise import fields

from src.models.db.base import BaseModel


class Player(BaseModel):
    nation = fields.TextField()
    player_name = fields.TextField()
    turn_played = fields.BooleanField()
