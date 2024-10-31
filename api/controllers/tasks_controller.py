import logging
import traceback
from asyncio import gather
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from telebot.apihelper import ApiTelegramException
from tortoise.transactions import in_transaction

from api.config import BOT
from api.errors import APIException
from api.models import UserGameState, User
from api.models.tasks.task import Task
from api.models.tasks.user_task import UserTask
from api.models.user import UserGameStats
from api.views.tasks.tasks import DailyTaskOut, SocialTaskOut, TaskClaimOut, TaskCompleteOut

DAILY_TASK_TYPE_THRESHOLD = 100
LAST_REFRESH_TIME = datetime.now()

class TasksController:
    @classmethod
    async def daily(cls, user_id: UUID) -> List[DailyTaskOut]:
        async with in_transaction() as connection:
            try:
                global LAST_REFRESH_TIME

                data_tasks = [
                    Task.filter(type__lt=DAILY_TASK_TYPE_THRESHOLD).only('uuid', 'type'),
                    UserTask.filter(user_fk=user_id, task_fk__type__lt=DAILY_TASK_TYPE_THRESHOLD).select_related('task_fk'),
                    UserGameStats.get(uuid=user_id).only(
                        'energy_spend',
                        'four_plus_matches_count',
                        'two_plus_matches_combo_count'
                    )
                ]
                (daily_tasks, user_daily_tasks, user_game_stats) = await gather(*data_tasks)
                if len(user_daily_tasks) < len(daily_tasks):
                    non_added_daily_tasks = [daily_task for daily_task in daily_tasks
                                             if not any(user_daily_task.task_fk_id == daily_task.uuid for user_daily_task in user_daily_tasks)]
                    add_daily_task_tasks = []
                    for non_added_daily_task in non_added_daily_tasks:
                        shift_value = max(0, (await cls.__get_daily_task_value__(user_game_stats, non_added_daily_task.type)))

                        add_daily_task_tasks.append(UserTask.create(
                            user_fk_id=user_id,
                            task_fk_id=non_added_daily_task.uuid,
                            shift_value=shift_value,
                            using_db=connection
                        ))

                    await gather(*add_daily_task_tasks)

                    user_daily_tasks = await UserTask.filter(user_fk=user_id, task_fk__type__lt=DAILY_TASK_TYPE_THRESHOLD).select_related('task_fk')


                now = datetime.now()
                refresh_tasks = LAST_REFRESH_TIME < now
                if refresh_tasks:
                    LAST_REFRESH_TIME = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=1) + timedelta(days=1)


                daily_tasks_out: List[DailyTaskOut] = []
                save_tasks_tasks = []
                for user_daily_task in user_daily_tasks:
                    if user_daily_task.progress_value < user_daily_task.task_fk.target_value or refresh_tasks:
                        user_task_updated_fields = []
                        value = max(0, (await cls.__get_daily_task_value__(user_game_stats, user_daily_task.task_fk.type)))
                        if refresh_tasks:
                            user_daily_task.progress_value = 0
                            user_daily_task.shift_value = value
                            user_task_updated_fields.extend(['progress_value', 'shift_value'])
                        elif user_daily_task.progress_value != value - user_daily_task.shift_value:
                            user_daily_task.progress_value = min(
                                value - user_daily_task.shift_value,
                                user_daily_task.task_fk.target_value
                            )
                            user_task_updated_fields.append('progress_value')

                        if len(user_task_updated_fields) > 0:
                            save_tasks_tasks.append(user_daily_task.save(update_fields=user_task_updated_fields, using_db=connection))


                    daily_tasks_out.append(DailyTaskOut(
                        type=user_daily_task.task_fk.type,
                        description=user_daily_task.task_fk.description,
                        progress=user_daily_task.progress_value,
                        target=user_daily_task.task_fk.target_value,
                        reward_type=user_daily_task.task_fk.reward_type,
                        reward=user_daily_task.task_fk.reward
                    ))

                if len(save_tasks_tasks) > 0:
                    await gather(*save_tasks_tasks)

                return daily_tasks_out
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def validate_rofl(cls, user_id: UUID) -> TaskCompleteOut:
        async with in_transaction() as connection:
            try:
                user_rofl_task = await UserTask.get(user_fk=user_id, task_fk__type=1).select_related('task_fk')

                if user_rofl_task.progress_value < user_rofl_task.task_fk.target_value:
                    user_rofl_task.progress_value += 1
                    await user_rofl_task.save(update_fields=['progress_value'], using_db=connection)

                return  TaskCompleteOut(
                    progress=user_rofl_task.progress_value,
                    target=user_rofl_task.task_fk.target_value
                )
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def social(cls, user_id: UUID) -> List[SocialTaskOut]:
        async with in_transaction() as connection:
            try:
                tasks_get_tasks = [
                    Task.filter(type__gt=DAILY_TASK_TYPE_THRESHOLD).only('uuid'),
                    UserTask.filter(user_fk=user_id, task_fk__type__gt=DAILY_TASK_TYPE_THRESHOLD).select_related('task_fk')
                ]
                (social_tasks, user_social_tasks) = await gather(*tasks_get_tasks)
                if len(user_social_tasks) < len(social_tasks):
                    non_added_social_tasks = [social_task for social_task in social_tasks
                                             if not any(user_social_task.task_fk_id == social_task.uuid for user_social_task in user_social_tasks)]
                    add_social_task_tasks = []
                    for non_added_social_task in non_added_social_tasks:
                        add_social_task_tasks.append(UserTask.create(
                            user_fk_id=user_id,
                            task_fk_id=non_added_social_task.uuid,
                            using_db=connection
                        ))

                    await gather(*add_social_task_tasks)

                    user_social_tasks = await UserTask.filter(user_fk=user_id, task_fk__type__gt=DAILY_TASK_TYPE_THRESHOLD).select_related('task_fk')


                social_tasks_out: List[SocialTaskOut] = []
                for social_task in user_social_tasks:
                    social_tasks_out.append(SocialTaskOut(
                        type=social_task.task_fk.type,
                        description=social_task.task_fk.description,
                        target_url=social_task.task_fk.target_url,
                        icon_url=social_task.task_fk.icon_url,
                        progress=social_task.progress_value,
                        target=social_task.task_fk.target_value,
                        reward_type=social_task.task_fk.reward_type,
                        reward=social_task.task_fk.reward
                    ))

                return social_tasks_out
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def validate_social(cls, user_id: UUID, task_type: int) -> TaskCompleteOut:
        async with in_transaction() as connection:
            try:
                if task_type < DAILY_TASK_TYPE_THRESHOLD:
                    raise Exception('Invalid task type')

                data_tasks = [
                    User.get(uuid=user_id).only('tg_id'),
                    (UserTask.get(user_fk=user_id, task_fk__type=task_type)
                     .select_related('task_fk').only('uuid', 'progress_value'))
                ]

                (user, user_task) = await gather(*data_tasks)

                completed_claimed = user_task.progress_value >= 1
                if completed_claimed:
                    return TaskCompleteOut(progress=user_task.progress_value, target=user_task.task_fk.target_value)

                if user_task.task_fk.target_tg_id == 'none':
                    user_task.progress_value = user_task.task_fk.target_value

                try:
                    BOT.get_chat_member(user_task.task_fk.target_tg_id, user.tg_id)
                    user_task.progress_value = user_task.task_fk.target_value
                except ApiTelegramException as e:
                    logging.warning(100, "Could not check")

                await user_task.save(update_fields=['progress_value'], using_db=connection)

                return TaskCompleteOut(progress=user_task.progress_value, target=user_task.task_fk.target_value)
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def claim(cls, user_id: UUID, task_type: int) -> TaskClaimOut:
        async with in_transaction() as connection:
            try:
                user_task = await UserTask.get(user_fk=user_id, task_fk__type=task_type).select_related('task_fk').only(
                    'uuid',
                    'progress_value',
                )

                not_completed_claimed = user_task.progress_value < user_task.task_fk.target_value
                if not_completed_claimed:
                    return TaskClaimOut(result=False)

                user_game_state = await UserGameState.get(uuid=user_id).only(
                    'uuid',
                    'hard_currency',
                    'soft_currency',
                    'energy'
                )
                updated_field: str
                if user_task.task_fk.reward_type == 1:
                    user_game_state.hard_currency += user_task.task_fk.reward
                    updated_field = 'hard_currency'
                elif user_task.task_fk.reward_type == 2:
                    user_game_state.soft_currency += user_task.task_fk.reward
                    updated_field = 'soft_currency'
                elif user_task.task_fk.reward_type == 3:
                    user_game_state.energy += user_task.task_fk.reward
                    updated_field = 'energy'

                user_task.progress_value = user_task.task_fk.target_value + 1
                save_tasks = [
                    user_task.save(update_fields=['progress_value'], using_db=connection),
                    user_game_state.save(update_fields=[updated_field], using_db=connection)
                ]

                await gather(*save_tasks)

                return TaskClaimOut(
                    result=True,
                    hard=user_game_state.hard_currency,
                    soft=user_game_state.soft_currency,
                    energy=user_game_state.energy
                )
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)


    @classmethod
    async def __get_daily_task_value__(cls, user_game_stats: UserGameStats, task_type: int) -> int:
        try:
            if task_type == 1: # IRL
                return 0
            if task_type == 2:  # Energy
                return user_game_stats.energy_spend
            if task_type == 4:  # Pop 4x
                return user_game_stats.four_plus_matches_count
            if task_type == 5:  # Pop 2xX
                return user_game_stats.two_plus_matches_combo_count

            return -1
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)
