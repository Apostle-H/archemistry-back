from email.policy import default
from uuid import uuid4

from more_itertools.recipes import unique
from tortoise import fields, models


class Task(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    type = fields.SmallIntField(default=0, index=True, unique=True)
    description = fields.CharField(max_length=64)
    target_value = fields.IntField(default=1)
    target_url = fields.CharField(max_length=128, default='none')
    target_tg_id = fields.CharField(max_length=32, default='none')
    icon_url = fields.CharField(max_length=128, default='none')
    reward_type = fields.SmallIntField(default=0)
    reward = fields.IntField(default=0)

    class Meta:
        table = 'task'