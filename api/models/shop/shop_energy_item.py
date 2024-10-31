from uuid import uuid4

from more_itertools.recipes import unique
from tortoise import fields, models


class ShopEnergyItem(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    type = fields.IntField(default=0, index=True, unique=True)
    amount = fields.IntField(default=0)
    cost = fields.IntField(default=0)

    class Meta:
        table = 'shop_energy_item'