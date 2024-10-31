from uuid import uuid4
from tortoise import fields, models


class Referral(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    referred_user_fk = fields.ForeignKeyField(
        'models.User', related_name='referrals', index=True, on_delete=fields.CASCADE
    )
    referred_by_user_fk = fields.ForeignKeyField(
        'models.User', related_name='referred_by_referrals', index=True, on_delete=fields.CASCADE
    )

    class Meta:
        table = 'referral'
