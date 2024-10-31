import logging
import math
import random
import traceback
from datetime import datetime
from asyncio import gather
from itertools import chain
from typing import List
from uuid import UUID

import tortoise.timezone
from click import IntRange
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from api.config import GRID_SIZE_X, GRID_SIZE_Y, MATCH_SETS, MOVE_ENERGY_COST, ENERGY_REGENERATION_DELTA_IN_SECONDS, \
    ENERGY_REGENERATION_AMOUNT, MATCH_ELEMENT_SOFT_REWARD, MATCH_ELEMENT_SCORE_VALUE, MATCH_ELEMENT_SOFT_REFERRAL_BONUS
from api.errors import APIException
from api.models import MatchElement, MatchSlot
from api.models.user import UserGameState, UserGameStats
from api.views.common.vec2 import Vec2
from api.views.match.match import MatchElementOut, MatchUserSlotOut, MatchDirection, MatchMoveOut, MatchClearOut, \
    MatchEnergyRestoreOut


class MatchController:
    @classmethod
    async def match_elements(cls) -> List[MatchElementOut]:
        try:
            match_elements = await MatchElement.all()

            match_elements_out = []
            for match_element in match_elements:
                match_elements_out.append(MatchElementOut(
                    id=match_element.uuid,
                    title=match_element.title
                ))

            return match_elements_out
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def user_grid(cls, user_id: UUID) -> List[MatchUserSlotOut]:
        try:
            match_slots = await MatchSlot.filter(user_fk=user_id)

            match_slots_out = []
            for match_slot in match_slots:
                match_slots_out.append(MatchUserSlotOut(
                    pos=Vec2(x=match_slot.pos_x, y=match_slot.pos_y),
                    element_id=match_slot.match_element_fk_id
                ))

            return match_slots_out
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def restore_energy(cls, user_id) -> MatchEnergyRestoreOut:
        async with in_transaction() as connection:
            try:
                user_game_state = await UserGameState.get(uuid=user_id).only(
                    'uuid',
                    'energy',
                    'max_energy',
                    'last_restore_time'
                )

                updated_fields = []

                now = datetime.now(tz=tortoise.timezone.get_default_timezone())
                delta = now - user_game_state.last_restore_time
                delta_in_seconds = delta.total_seconds()

                user_game_state.last_restore_time = now
                updated_fields.append('last_restore_time')

                if user_game_state.energy < user_game_state.max_energy:
                    regenerate_times = math.floor(delta_in_seconds / ENERGY_REGENERATION_DELTA_IN_SECONDS)
                    if regenerate_times > 0:
                        regenerate_amount = regenerate_times * ENERGY_REGENERATION_AMOUNT
                        user_game_state.energy = min(user_game_state.energy + regenerate_amount, user_game_state.max_energy)
                        updated_fields.append('energy')

                await user_game_state.save(update_fields=updated_fields)
                return MatchEnergyRestoreOut(energy=user_game_state.energy, max_energy=user_game_state.max_energy)
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def move(cls, user_id: UUID, pos: Vec2, direction: MatchDirection) -> MatchMoveOut:
        async with in_transaction() as connection:
            try:
                if pos.x < 0 or pos.x >= GRID_SIZE_X or pos.y < 0 or pos.y >= GRID_SIZE_Y:
                    return MatchMoveOut(result=False)

                to_pos = Vec2(x=pos.x, y=pos.y)
                if direction == MatchDirection.LEFT:
                    to_pos.x -= 1
                elif direction == MatchDirection.UP:
                    to_pos.y += 1
                elif direction == MatchDirection.RIGHT:
                    to_pos.x += 1
                elif direction == MatchDirection.DOWN:
                    to_pos.y -= 1

                if to_pos.x < 0 or to_pos.x >= GRID_SIZE_X or to_pos.y < 0 or to_pos.y >= GRID_SIZE_Y:
                    return MatchMoveOut(result=False)

                get_elements_tasks = [
                    MatchSlot.get(user_fk=user_id, pos_x=pos.x, pos_y=pos.y),
                    MatchSlot.get(user_fk=user_id, pos_x=to_pos.x, pos_y=to_pos.y),
                    UserGameState.get(uuid=user_id).only(
                        'uuid',
                        'energy',
                        'match_combo_streak',
                        'last_move_match_combo_streak',
                        'in_clearing_match_combo_streak'
                    ),
                    UserGameStats.get(uuid=user_id).only('uuid', 'energy_spend')
                ]
                (slot, to_slot, user_game_state, user_game_stats) = await gather(*get_elements_tasks)

                if user_game_state.energy <= 0:
                    return MatchMoveOut(result=False)

                slot_element_id = slot.match_element_fk_id
                to_slot_element_id = to_slot.match_element_fk_id

                slot.match_element_fk_id = to_slot_element_id
                to_slot.match_element_fk_id = slot_element_id

                user_game_state_updated_fields = ['energy', 'last_move_match_combo_streak', 'in_clearing_match_combo_streak']
                user_game_state.energy -= MOVE_ENERGY_COST
                user_game_stats.energy_spend += MOVE_ENERGY_COST
                if user_game_state.last_move_match_combo_streak == user_game_state.match_combo_streak:
                    user_game_state.match_combo_streak = 0
                    user_game_state_updated_fields.append('match_combo_streak')
                user_game_state.last_move_match_combo_streak = user_game_state.match_combo_streak
                user_game_state.in_clearing_match_combo_streak = 0

                move_elements_task = [
                    slot.save(update_fields=['match_element_fk_id'], using_db=connection),
                    to_slot.save(update_fields=['match_element_fk_id'], using_db=connection),
                    user_game_state.save(update_fields=user_game_state_updated_fields, using_db=connection),
                    user_game_stats.save(update_fields=['energy_spend'], using_db=connection)
                ]
                await gather(*move_elements_task)

                return MatchMoveOut(result=True, energy=user_game_state.energy)
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def clear(cls, user_id: UUID, clusters: List[List[Vec2]]) -> MatchClearOut:
        try:
            check_clear_tasks = [cls.__check_clear__(user_id, cluster) for cluster in clusters]
            results = await gather(*check_clear_tasks)

            refresh_pos: List[MatchUserSlotOut] = []
            success_clusters = [cluster for index, cluster in enumerate(clusters) if results[index]]
            (soft, score) = (-1, -1)
            if len(success_clusters) > 0:
                cleared = list(chain.from_iterable(success_clusters))
                success_tasks = [
                    cls.__fill_cleared__(user_id, cleared),
                    cls.__score_rewards_write_stats__(user_id, success_clusters)
                ]
                (refresh_pos, (soft, score)) = await gather(*success_tasks)

            return MatchClearOut(results=results, refresh_pos=refresh_pos, soft=soft, score=score)
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def __check_clear__(cls, user_id: UUID, cluster: List[Vec2]) -> bool:
        try:
            min_vec2 = min(cluster, key=lambda vec2: vec2.length())
            minimized_cluster = [Vec2(x=vec2.x - min_vec2.x, y=vec2.y - min_vec2.y) for vec2 in cluster]
            sorted_cluster = sorted(minimized_cluster, key=lambda vec2: (vec2.y, vec2.x))

            matches_shape = False
            for match_set in MATCH_SETS:
                if match_set != sorted_cluster:
                    continue

                matches_shape = True
                break

            if not matches_shape:
                return False

            pos_queries = [Q(pos_x=vec2.x, pos_y=vec2.y) for vec2 in cluster]
            combined_pos_query = Q()
            for query in pos_queries:
                combined_pos_query |= query

            slots = await MatchSlot.filter(user_fk=user_id).filter(combined_pos_query).only('match_element_fk_id')

            match_element_id = slots[0].match_element_fk_id
            matches_type = all(slot.match_element_fk_id == match_element_id for slot in slots)

            return matches_type
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def __fill_cleared__(cls, user_id: UUID, cleared: List[Vec2]) -> List[MatchUserSlotOut]:
        async with in_transaction() as connection:
            try:
                clear_columns = {}
                for pos in cleared:
                    if pos.x in clear_columns:
                        if pos.y < clear_columns[pos.x].min:
                            clear_columns[pos.x].min = pos.y
                        elif pos.y > clear_columns[pos.x].max - 1:
                            clear_columns[pos.x].max = pos.y + 1
                    else:
                        clear_columns[pos.x] = IntRange(pos.y, pos.y + 1)

                refresh_pos: List[MatchUserSlotOut] = []
                elements_ids = [element.uuid for element in (await MatchElement.all().only('uuid'))]

                combined_pos_query = Q()
                for column, y_range in clear_columns.items():
                    for y in range(int(y_range.min), GRID_SIZE_Y):
                        combined_pos_query |= Q(pos_x=column, pos_y=y)

                affected_slots = await MatchSlot.filter(user_fk=user_id).filter(combined_pos_query)
                affected_slots_dict = {(slot.pos_x, slot.pos_y): slot for slot in affected_slots}

                for clear_column, clear_range in clear_columns.items():
                    clear_length = int(clear_range.max - clear_range.min)
                    for y in range(int(clear_range.min), GRID_SIZE_Y):
                        new_element_id: UUID
                        if y + clear_length < GRID_SIZE_Y:
                            new_element_id = affected_slots_dict[(clear_column, y + clear_length)].match_element_fk_id
                        else:
                            new_element_id = random.choice(elements_ids)

                        affected_slots_dict[(clear_column, y)].match_element_fk_id = new_element_id

                        refresh_pos.append(MatchUserSlotOut(
                            pos=Vec2(x=clear_column, y=y),
                            element_id=new_element_id
                        ))

                save_tasks = [slot.save(update_fields=['match_element_fk_id'], using_db=connection) for slot in affected_slots]

                await gather(*save_tasks)

                return refresh_pos
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)

    @classmethod
    async def __score_rewards_write_stats__(cls, user_id: UUID, cleared_clusters: List[List[Vec2]]) -> (int, int):
        async with in_transaction() as connection:
            try:
                user_data_tasks = [
                    UserGameState.get(uuid=user_id).only(
                        'uuid',
                        'soft_currency',
                        'score',
                        'match_combo_streak',
                        'in_clearing_match_combo_streak'
                    ),
                    UserGameStats.get(uuid=user_id).only(
                        'uuid',
                        'referrals_count',
                        'matches_count',
                        'four_plus_matches_count',
                        'two_plus_matches_combo_count',
                        'max_match_combo_streak'
                    )
                ]
                (user_game_state, user_game_stats) = await gather(*user_data_tasks)
                user_game_state_updated_fields = [
                    'soft_currency', 'score', 'match_combo_streak', 'in_clearing_match_combo_streak'
                ]
                user_game_stats_updated_fields = ['matches_count']

                soft_up = 0
                score_up = 0
                match_element_full_cost = (MATCH_ELEMENT_SOFT_REWARD + (MATCH_ELEMENT_SOFT_REFERRAL_BONUS * user_game_stats.referrals_count))
                for cluster in cleared_clusters:
                    cluster_size = len(cluster)
                    soft_up += match_element_full_cost * 3 * (math.pow(2, cluster_size - 3))
                    score_up += (cluster_size - 2) * MATCH_ELEMENT_SCORE_VALUE

                user_game_state.soft_currency += soft_up
                user_game_state.score += score_up


                for cluster in cleared_clusters:
                    user_game_state.match_combo_streak += 1
                    user_game_state.in_clearing_match_combo_streak += 1
                    user_game_stats.matches_count += 1

                    if user_game_state.in_clearing_match_combo_streak == 2:
                        user_game_stats.two_plus_matches_combo_count += 1
                        user_game_stats_updated_fields.append('two_plus_matches_combo_count')

                    if len(cluster) < 4:
                        continue

                    user_game_stats.four_plus_matches_count += 1
                    user_game_stats_updated_fields.append('four_plus_matches_count')


                if user_game_state.match_combo_streak > user_game_stats.max_match_combo_streak:
                    user_game_stats.max_match_combo_streak = user_game_state.match_combo_streak
                    user_game_stats_updated_fields.append('max_match_combo_streak')

                save_tasks = [
                    user_game_state.save(update_fields=user_game_state_updated_fields, using_db=connection),
                    user_game_stats.save(update_fields=user_game_stats_updated_fields, using_db=connection)
                ]
                await gather(*save_tasks)

                return user_game_state.soft_currency, user_game_state.score
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)
