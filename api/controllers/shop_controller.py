import logging
import traceback
from asyncio import gather
from typing import List
from uuid import UUID

from tortoise.transactions import in_transaction

from api.errors import APIException
from api.models import ShopEnergyItem, UserGameState
from api.views.shop.shop import ShopEnergyItemOut, BuyEnergyItemOut


class ShopController:
    @classmethod
    async def energy_items(cls) -> List[ShopEnergyItemOut]:
        try:
            energy_items = await ShopEnergyItem.all()

            energy_items_out: List[ShopEnergyItemOut] = []
            for shop_item in energy_items:
                energy_items_out.append(ShopEnergyItemOut(
                    type=shop_item.type,
                    amount=shop_item.amount,
                    cost=shop_item.cost
                ))

            return energy_items_out
        except Exception as e:
            logging.error(f'{e} {traceback.format_exc()}')
            raise APIException('Not found', 404)

    @classmethod
    async def buy_energy_item(cls, user_id: UUID, item_type: int) -> BuyEnergyItemOut:
        async with in_transaction() as connection:
            try:
                data_tasks = [
                    UserGameState.get(uuid=user_id).only('uuid', 'soft_currency', 'energy'),
                    ShopEnergyItem.get(type=item_type).only('amount', 'cost')
                ]

                (user_game_state, energy_item) = await gather(*data_tasks)

                if user_game_state.soft_currency < energy_item.cost:
                    return BuyEnergyItemOut(result=False)

                user_game_state.soft_currency -= energy_item.cost
                user_game_state.energy += energy_item.amount

                await user_game_state.save(update_fields=['soft_currency', 'energy'], using_db=connection)

                return BuyEnergyItemOut(result=True, soft=user_game_state.soft_currency, energy=user_game_state.energy)
            except Exception as e:
                logging.error(f'{e} {traceback.format_exc()}')
                raise APIException('Not found', 404)
