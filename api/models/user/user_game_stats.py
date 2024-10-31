from uuid import uuid4
from tortoise import fields, models
from tortoise.indexes import Index


class UserGameStats(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    referrals_count = fields.IntField(default=0)
    energy_spend = fields.BigIntField(default=0)
    matches_count = fields.BigIntField(default=0)
    four_plus_matches_count = fields.BigIntField(default=0)
    two_plus_matches_combo_count = fields.BigIntField(default=0)
    max_match_combo_streak = fields.BigIntField(default=0)

    class Meta:
        table = 'user_game_stats'