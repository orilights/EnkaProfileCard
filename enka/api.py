import json
import io

from loguru import logger
import requests
from PIL import Image

from .exception import *
from .utils import read_cache, to_base64, write_cache

user_agent = 'GameCard/v1-alpha'
header_webp = 'data:image/webp;base64,'
enka_ui_base = 'https://enka.network/ui/'


def get_profile_icon(game, icon_id, size=128):
    if isinstance(icon_id, str) and icon_id.startswith('char'):
        return get_character_icon(game, icon_id[4:], size=size)
    cache_key = f'image/profile_{game}_{icon_id}_{size}'
    if cache := read_cache(cache_key):
        return cache
    avatar_dict = json.load(
        open(f'./assets/{game}.pfps.json', 'r', encoding='utf-8'))
    if avatar_data := avatar_dict.get(str(icon_id), None):
        filename = avatar_data['iconPath'] + '.png'
        url = enka_ui_base + filename
        r = requests.get(url, headers={'User-Agent': user_agent})
        i = Image.open(io.BytesIO(r.content))
        i = i.resize((size, size))
        image_data = io.BytesIO()
        i.save(image_data, format='webp')
        image_data = header_webp + to_base64(image_data.getvalue())
        write_cache(cache_key, image_data, -1)
        return image_data
    else:
        return None


def get_character_icon(game, character_id, costume_id=0, size=64):
    cache_key = f'image/character_{game}_{character_id}_{costume_id}_{size}'
    if cache := read_cache(cache_key):
        return cache
    charactor_dict = json.load(
        open(f'./assets/{game}.characters.json', 'r', encoding='utf-8'))
    if char_data := charactor_dict.get(str(character_id), None):
        if costume_id:
            filename = char_data['Costumes'][str(
                costume_id)]['sideIconName'].replace('Side_', '') 
        else:
            filename = char_data['SideIconName'].replace('Side_', '')
        if size == 128:
            filename = filename + '_Circle'
        url = enka_ui_base + filename + '.png'
        r = requests.get(url, headers={'User-Agent': user_agent})
        i = Image.open(io.BytesIO(r.content))
        i = i.resize((size, size))
        image_data = io.BytesIO()
        i.save(image_data, format='webp')
        image_data = header_webp + to_base64(image_data.getvalue())
        write_cache(cache_key, image_data, -1)
        return image_data
    else:
        return None


def get_genshin(uid):
    if player_info := read_cache(f'profile/genshin_{uid}'):
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
        if data.get('towerFloorIndex', None) is None:
            abyss = '未知'
        else:
            abyss = f'{data["towerFloorIndex"]}-{data["towerLevelIndex"]}'
        if profilePictureId := data['profilePicture'].get('id', None):
            pass
        else:
            logger.warning(f'[get_info]game:genshin uid:{uid} no profilePictureId, use avatarId instead')
            if avatarId := data['profilePicture'].get('avatarId', None):
                profilePictureId = f'char{avatarId}'
            else:
                profilePictureId = 1
        player_info = {
            'uid': uid,
            'nickname': data.get('nickname', '未知'),
            'level': data['level'],
            'worldLevel': data.get('worldLevel', '未知'),
            'achievement': data.get('finishAchievementNum', '未知'),
            'abyss': abyss,
            'avatars': data.get('showAvatarInfoList', []),
            'profilePictureId': profilePictureId,
        }
        write_cache(f'profile/genshin_{uid}', json.dumps(player_info),
                    3600 * 24)
        logger.debug(
            f'[get_info] game:genshin uid:{uid} player_info:{player_info}')
        return player_info
    except Exception as e:
        raise NetworkError(e)
