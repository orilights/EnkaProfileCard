import base64
import json
import os
import io
import time

from loguru import logger
import requests
from PIL import Image

from exception import *
from utils import read_cache, to_base64, write_cache

user_agent = 'GameCard/v1-alpha'
header_webp = 'data:image/webp;base64,'
enka_ui_base = 'https://enka.network/ui/'

profile_size = 128
character_size = 64


def get_profile_icon(game, icon_id):
    if cache := read_cache(f'image/profile_{game}_{icon_id}'):
        return cache
    avatar_dict = json.load(
        open(f'./assets/{game}.pfps.json', 'r', encoding='utf-8'))
    if avatar_data := avatar_dict.get(str(icon_id), None):
        filename = avatar_data['iconPath'] + '.png'
        url = enka_ui_base + filename
        r = requests.get(url, headers={'User-Agent': user_agent})
        i = Image.open(io.BytesIO(r.content))
        i = i.resize((profile_size, profile_size))
        image_data = io.BytesIO()
        i.save(image_data, format='webp')
        image_data = header_webp + to_base64(image_data.getvalue())
        write_cache(f'image/profile_{game}_{icon_id}', image_data, -1)
        return image_data
    else:
        return None


def get_character_icon(game, character_id, costume_id=0):
    if cache := read_cache(
            f'image/character_{game}_{character_id}_{costume_id}'):
        return cache
    charactor_dict = json.load(
        open(f'./assets/{game}.characters.json', 'r', encoding='utf-8'))
    if char_data := charactor_dict.get(str(character_id), None):
        if costume_id:
            filename = char_data['Costumes'][str(
                costume_id)]['sideIconName'].replace('Side_', '') + '.png'
        else:
            filename = char_data['SideIconName'].replace('Side_', '') + '.png'
        url = enka_ui_base + filename
        r = requests.get(url, headers={'User-Agent': user_agent})
        i = Image.open(io.BytesIO(r.content))
        i = i.resize((character_size, character_size))
        image_data = io.BytesIO()
        i.save(image_data, format='webp')
        image_data = header_webp + to_base64(image_data.getvalue())
        write_cache(f'image/character_{game}_{character_id}_{costume_id}',
                    image_data, -1)
        return image_data
    else:
        return None


def get_genshin(uid):
    if player_info := read_cache(f'genshin_{uid}'):
        logger.info(f'[get_info]game:genshin uid:{uid} cache hit')
        return json.loads(player_info)
    api = 'https://enka.network/api/uid/{uid}?info'
    logger.info(f'[get_info]game:genshin uid:{uid}')
    try:
        r = requests.get(api.format(uid=uid),
                         headers={'User-Agent': user_agent})
        logger.debug(
            f'[get_info]game:genshin uid:{uid} status_code:{r.status_code}')
        if r.status_code != 200:
            if r.status_code == 400:
                raise RequestError('UID invalid')
            elif r.status_code == 404:
                raise RequestError('UID not found')
            elif r.status_code == 424:
                raise RequestError('Game or Enka.network maintenance')
            elif r.status_code == 429:
                raise RequestError('Rate limit exceeded')
            elif r.status_code == 500:
                raise ServerError('Internal server error')
            elif r.status_code == 503:
                raise ServerError('Something went wrong')
            else:
                raise ServerError('Unknown error')
        data = r.json()['playerInfo']
        player_info = {
            'uid': uid,
            'nickname': data['nickname'],
            'level': data['level'],
            'worldLevel': data['worldLevel'],
            'achievement': data['finishAchievementNum'],
            'abyss': f'{data["towerFloorIndex"]}-{data["towerLevelIndex"]}',
            'avatars': data['showAvatarInfoList'],
            'profilePictureId': data['profilePicture']['id'],
        }
        write_cache(f'genshin_{uid}', json.dumps(player_info), 3600 * 24)
        logger.debug(
            f'[get_info] game:genshin uid:{uid} player_info:{player_info}')
        return player_info
    except Exception as e:
        raise NetworkError(e)
