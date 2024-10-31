import logging
import traceback
from asyncio import gather
from typing import List
from uuid import UUID

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from api.config import REFERRAL_ENERGY_REWARD
from api.errors import APIException
from api.models import User, UserGameState, UserGameStats
from api.models.referral.referral import Referral
from api.views.referral.referral import ReferralOut


class ReferralController:
    @classmethod
    async def user_all(cls, user_id: UUID) -> List[ReferralOut]:
        try:
            referrals = await Referral.filter(referred_by_user_fk_id=user_id).select_related('referred_user_fk')

            referrals_game_states_query = [Q(uuid=referral.referred_user_fk_id) for referral in referrals]
            combined_referrals_game_states_query = Q()
            for query in referrals_game_states_query:
                combined_referrals_game_states_query |= query

            referrals_game_states = await UserGameState.filter(combined_referrals_game_states_query).only('uuid', 'score')
            referrals_scores_dict = {referral_game_state.uuid: referral_game_state.score for referral_game_state in referrals_game_states}
            referrals_out: List[ReferralOut] = []
            for referral in referrals:
                referrals_out.append(ReferralOut(
                    username=referral.referred_user_fk.username,
                    score=referrals_scores_dict[referral.referred_user_fk_id]
                ))

            return referrals_out
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def new(cls, referred_tg_id: int, referred_by_tg_id: int) -> bool:
        async with in_transaction() as connection:
            try:
                if referred_tg_id == referred_by_tg_id:
                    return False

                exists_tasks = [
                    User.exists(tg_id=referred_tg_id),
                    User.exists(tg_id=referred_by_tg_id)
                ]

                if any(not exists for exists in (await gather(*exists_tasks))):
                    return False

                users_tasks = [
                    User.get(tg_id=referred_tg_id).only('uuid'),
                    User.get(tg_id=referred_by_tg_id).only('uuid')
                ]
                (referred_user, referred_by_user) = await gather(*users_tasks)
                referred_id = referred_user.uuid
                referred_by_id = referred_by_user.uuid

                referral_exits_tasks = [
                    Referral.exists(referred_user_fk=referred_id, referred_by_user_fk=referred_by_id),
                    Referral.exists(referred_user_fk=referred_by_id, referred_by_user_fk=referred_id)
                ]
                referral_exits = await gather(*referral_exits_tasks)
                if any(referral_exits):
                    return False

                data_tasks = [
                    UserGameState.get(uuid=referred_by_id).only('uuid', 'max_energy'),
                    UserGameStats.get(uuid=referred_by_id).only('uuid', 'referrals_count')
                ]

                (referred_game_state, referred_game_stats) = await gather(*data_tasks)
                referred_game_state.max_energy += REFERRAL_ENERGY_REWARD
                referred_game_stats.referrals_count += 1

                success_tasks = [
                    Referral.create(referred_user_fk_id=referred_id, referred_by_user_fk_id=referred_by_id),
                    referred_game_state.save(update_fields=['max_energy'], using_db=connection),
                    referred_game_stats.save(update_fields=['referrals_count'], using_db=connection)
                ]

                await gather(*success_tasks)

                return True
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)
