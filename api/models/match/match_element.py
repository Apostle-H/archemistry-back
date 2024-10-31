from uuid import uuid4
from tortoise import fields, models


class MatchElement(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    title = fields.CharField(max_length=20)

    class Meta:
        table = 'match_element'