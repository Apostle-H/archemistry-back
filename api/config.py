import json
import os

import telebot
from dotenv import load_dotenv

from api.views.common.vec2 import Vec2

load_dotenv()

debug = os.getenv("DEBUG", False)

db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT")
db_host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB")
db_url = f"postgres://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
print (db_url)
TORTOISE_ORM = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": ["api.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

BOT = telebot.TeleBot(os.getenv("BOT_TOKEN"))

with open('api/consts.json', 'r') as file:
    consts_json = file.read()

consts_dict = json.loads(consts_json)

MAX_ENERGY = int(consts_dict['max_energy'])
MOVE_ENERGY_COST = int(consts_dict['move_energy_cost'])
ENERGY_REGENERATION_DELTA_IN_SECONDS = int(consts_dict['energy_regeneration_delta_in_seconds'])
ENERGY_REGENERATION_AMOUNT = int(consts_dict['energy_regeneration_amount'])

RATING_UPDATE_DELTA_IN_SECONDS = int(consts_dict['rating_update_delta_in_seconds'])

REFERRAL_ENERGY_REWARD = int(consts_dict['referral_energy_reward'])

GRID_SIZE_X = int(consts_dict['grid_size_x'])
GRID_SIZE_Y = int(consts_dict['grid_size_y'])
MATCH_ELEMENT_SOFT_REWARD = int(consts_dict['match_element_soft_reward'])
MATCH_ELEMENT_SOFT_REFERRAL_BONUS = int(consts_dict['match_element_soft_referral_bonus'])
MATCH_ELEMENT_SCORE_VALUE = consts_dict['match_element_score_value']
MATCH_SETS = [
        [Vec2(x=point['x'], y=point['y']) for point in match_set]
        for match_set in consts_dict['match_sets']
    ]
