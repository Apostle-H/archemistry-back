import logging
import traceback
from asyncio import gather
from datetime import datetime
from typing import List
from uuid import UUID

from tortoise import Tortoise

from api.config import RATING_UPDATE_DELTA_IN_SECONDS
from api.errors import APIException
from api.models import User
from api.views.rating.rating import RatingOut, UserRating

TOP_FOUR: List[UserRating]

last_update_time: datetime = None

class RatingController:
    @classmethod
    async def score(cls, user_id: UUID) -> RatingOut:
        try:
            global TOP_FOUR
            global last_update_time
            connection = Tortoise.get_connection('default')

            if last_update_time is None or (datetime.now(tz=last_update_time.tzinfo) - last_update_time).total_seconds() > RATING_UPDATE_DELTA_IN_SECONDS:
                (_, top_four_raw) = await connection.execute_query('SELECT u.username, ugs.score FROM user_game_state ugs JOIN "user" u ON u.uuid = ugs.uuid ORDER BY ugs.score DESC LIMIT 4;')
                TOP_FOUR = [UserRating(username=top['username'], score=top['score'], place=index + 1) for (index, top) in enumerate(top_four_raw)]

                last_update_time = datetime.now()

            user_place_tasks = [
                User.get(uuid=user_id).only('username'),
                connection.execute_query(
                    """
                    SELECT uuid, score, 
                       (
                            SELECT COUNT(*) 
                            FROM user_game_state 
                            WHERE score > ugs.score
                        ) + 1 AS place
                    FROM user_game_state AS ugs
                    WHERE uuid = '{}';
                    """.format(user_id)
                )
            ]
            (user, (_, self_raw)) = await gather(*user_place_tasks)
            self = UserRating(username=user.username, score=self_raw[0]['score'], place=self_raw[0]['place'])

            return RatingOut(top_four=TOP_FOUR, self=self)
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)


