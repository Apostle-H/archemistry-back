from uuid import uuid4
from tortoise import fields, models


class User(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    tg_id = fields.BigIntField(index=True, unique=True)
    is_premium = fields.BooleanField(null=True)
    username = fields.CharField(max_length=128, null=True)

    class Meta:
        table = 'user'