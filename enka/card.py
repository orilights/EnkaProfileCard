import os

from loguru import logger

from .api import get_profile_icon, get_character_icon
from .exception import *
from .utils import md5, read_cache, to_base64, get_ts, write_cache, timeit

default_texts = '0123456789UIDLV成就总数深境螺旋展柜无角色-PoweredbyEnka.Network'
header_woff2 = 'data:application/font-woff2;base64,'
header_webp = 'data:image/webp;base64,'


@timeit('generate_card')
def generate_card(game, player_info):
    ts = get_ts()
    logger.info(f'[generate_card]game:{game} uid:{player_info["uid"]}')
    template = open(f'./template/{game}.svg', encoding='utf-8').read()
    game_font = f'./assets/{game}.font.ttf'
    nickname = player_info['nickname']
    if font := read_cache(f'font/{game}_{md5(nickname)}'):
        logger.info(
            f'[generate_card]game:{game} uid:{player_info["uid"]} font cache hit'
        )
    else:
        text = default_texts + nickname
        os.system(
            f'pyftsubset {game_font} --text="{text}" --flavor=woff2 --output-file=./tmp_{ts}'
        )
        font = to_base64(f'./tmp_{ts}')
        write_cache(f'font/{game}_{md5(nickname)}', font, -1)
        os.remove(f'./tmp_{ts}')
    template = template.replace(
        '{background}', header_webp + to_base64(f'./template/{game}.webp'))
    template = template.replace('{font}', header_woff2 + font)
    template = template.replace('{nickname}', player_info['nickname'])
    template = template.replace('{uid}', str(player_info['uid']))
    template = template.replace('{level}', str(player_info['level']))
    template = template.replace('{worldLevel}', str(player_info['worldLevel']))
    template = template.replace('{achievement}',
                                str(player_info['achievement']))
    template = template.replace('{abyss}', player_info['abyss'])
    template = template.replace(
        '{avatar}', get_profile_icon(game, player_info['profilePictureId']))
    if len(player_info['avatars']) == 0:
        template = template.replace('{characters}', '展柜无角色')
    else:
        avatars = ''
        for avatar in player_info['avatars']:
            icon_name = get_character_icon(game, avatar['avatarId'],
                                           avatar.get('costumeId', 0))
            avatars += f'<img class="avatar character" src="{icon_name}"/>'
        template = template.replace('{characters}', avatars)
    os.makedirs(f'./cache/card', exist_ok=True)
    open(f'./cache/card/{game}_{player_info["uid"]}.svg',
         'w',
         encoding='utf-8').write(template)
