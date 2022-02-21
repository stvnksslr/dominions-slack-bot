from tortoise import fields, models


class Game(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=120, null=False)
    port = fields.SmallIntField(null=False)
    active = fields.BooleanField(default=True, null=False)
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now=True)
