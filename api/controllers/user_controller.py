import logging
import traceback
from asyncio import gather
import random
from uuid import UUID, uuid4
from tortoise.transactions import in_transaction

from api.config import GRID_SIZE_X, GRID_SIZE_Y, MAX_ENERGY
from api.controllers.referral_controller import ReferralController
from api.errors import APIException
from api.models import User, MatchElement, UserGameState
from api.models.match.match_slot import MatchSlot
from api.models.user import UserGameStats
from api.views.user.user import UserGameStateOut


class UserController:
    @classmethod
    async def user_login(cls, tg_id: int, is_premium: bool, username: str, referred_by_tg_id: int) -> UUID:
        try:
            user_exists = await User.filter(tg_id=tg_id).exists()
            if user_exists:
                return await cls.__load_user__(tg_id)
            else:
                return await cls.__create_user__(tg_id, is_premium, username, referred_by_tg_id)
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def __load_user__(cls, tg_id: int) -> UUID:
        try:
            user_id = (await User.get(tg_id=tg_id).only('uuid')).uuid
            return user_id
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def __create_user__(cls, tg_id: int, is_premium: bool, username: str, referred_by_tg_id: int) -> UUID:
        async with in_transaction() as connection:
            try:
                user_id = uuid4()
                username = "unknown" if username is None or username == "" else username
                get_create_tasks = [
                    User.create(uuid=user_id, tg_id=tg_id, is_premium=is_premium, username=username, using_db=connection),
                    UserGameState.create(uuid=user_id, energy=MAX_ENERGY, max_energy=MAX_ENERGY, using_db=connection),
                    UserGameStats.create(uuid=user_id, using_db=connection),
                    MatchElement.all().only('uuid')
                ]
                (user, user_game_state, user_game_stats, elements) = await gather(*get_create_tasks)

                elements_ids = [match_element.uuid for match_element in elements]
                match_element_tasks = []
                for x in range(0, GRID_SIZE_X):
                    for y in range(0, GRID_SIZE_Y):
                        match_element_tasks.append(MatchSlot.create(
                            pos_x=x,
                            pos_y=y,
                            user_fk_id=user_id,
                            match_element_fk_id=random.choice(elements_ids),
                            using_db=connection
                        ))

                await gather(*match_element_tasks, ReferralController.new(tg_id, referred_by_tg_id))

                return user_id
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def user_game_state(cls, user_id) -> UserGameStateOut:
        try:
            user_game_state = await UserGameState.get(uuid=user_id)

            return UserGameStateOut(
                hard=user_game_state.hard_currency,
                soft=user_game_state.soft_currency,
                score=user_game_state.score,
                energy=user_game_state.energy,
                max_energy=user_game_state.max_energy
            )
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)
