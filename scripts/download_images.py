import json
import time

from enka.api import get_character_icon, get_profile_icon

characters = json.load(
    open('./assets/genshin.characters.json', 'r', encoding='utf-8'))

for character_id in characters:
    character_data = characters[character_id]
    get_character_icon('genshin', character_id)
    if costumes := character_data.get('Costumes'):
        for costume_id in costumes:
            get_character_icon('genshin', character_id, costume_id)
    time.sleep(0.5)

profiles = json.load(open('./assets/genshin.pfps.json', 'r', encoding='utf-8'))

for profile_id in profiles:
    get_profile_icon('genshin', profile_id)
    time.sleep(0.5)
