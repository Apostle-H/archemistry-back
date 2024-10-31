from uuid import uuid4

from pygments.lexer import default
from tortoise import fields, models

class UserGameState(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    hard_currency = fields.BigIntField(default=0)
    soft_currency = fields.BigIntField(default=0)
    score = fields.BigIntField(default=0, index=True)
    energy = fields.IntField(default=0)
    max_energy = fields.IntField(default=0)
    last_restore_time = fields.DatetimeField(auto_now_add=True)
    match_combo_streak = fields.IntField(default=0)
    last_move_match_combo_streak = fields.IntField(default=0)
    in_clearing_match_combo_streak = fields.IntField(default=0)


    class Meta:
        table = 'user_game_state'