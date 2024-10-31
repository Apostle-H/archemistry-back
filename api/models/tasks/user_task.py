from uuid import uuid4
from tortoise import fields, models


class UserTask(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    task_fk = fields.ForeignKeyField(
        'models.Task', related_name='tasks', index=True, on_delete=fields.CASCADE
    )
    user_fk = fields.ForeignKeyField(
        'models.User', related_name='users', index=True, on_delete=fields.CASCADE
    )
    shift_value = fields.IntField(default=0)
    progress_value = fields.IntField(default=0)

    class Meta:
        table = 'user_task'