from fastapi.responses import FileResponse
from fastapi import FastAPI
from loguru import logger
from enka.card import generate_card
from enka.api import *

support_game = ['genshin']

app = FastAPI()


@app.get("/")
async def root():
    return {
        "name": "EnkaProfileCard",
        "support_game": support_game,
        "versoon": 'dev',
        "docs": "/docs"
    }
    
@app.get('/refresh')
def refresh_data():
    logger.info('[refresh_data] try to refresh data')
    if genshin_characters := get_genshin_characters():
        logger.info('[refresh_data] downloaded genshin characters data')
        open('./assets/genshin.characters.json', 'w', encoding='utf-8').write(json.dumps(genshin_characters, ensure_ascii=False, indent=4))
    if genshin_pfps := get_genshin_pfps():
        logger.info('[refresh_data] downloaded genshin pfps data')
        open('./assets/genshin.pfps.json', 'w', encoding='utf-8').write(json.dumps(genshin_pfps, ensure_ascii=False, indent=4))


@app.get("/{game}/{uid}.png")
def get_card(game: str, uid: int):
    if game not in support_game:
        return {"msg": "game not support"}
    try:
        player_info = get_genshin(uid)
    except Exception as e:
        return {"msg": f"get player info error: {e}"}
    if not player_info:
        return {"msg": "player not found"}
    try:
        generate_card(game, player_info)
        return FileResponse(f'./cache/card/{game}_{uid}.svg',
                            media_type='image/svg+xml')
    except Exception as e:
        return {"msg": f"generate card error: {e}"}
