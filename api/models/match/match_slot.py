from uuid import uuid4
from tortoise import fields, models


class MatchSlot(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    pos_x = fields.IntField(default=0)
    pos_y = fields.IntField(default=0)
    user_fk = fields.ForeignKeyField(
        'models.User', related_name='user_match_slot', index=True, on_delete=fields.CASCADE
    )
    match_element_fk = fields.ForeignKeyField(
        'models.MatchElement', related_name='user_match_element', index=True, on_delete=fields.CASCADE
    )

    class Meta:
        table = 'match_slot'