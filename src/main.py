from fastapi.responses import FileResponse
from card import generate_card
from enka import get_genshin
from fastapi import FastAPI

support_game = ['genshin']


app = FastAPI()


@app.get("/")
async def root():
    return {"name": "GameProfileCard",
            "support_game": support_game}
    
@app.get("/{game}/{uid}.png",responses={
    200: {
        "description": "Return the card",
        "content": {"image/svg+xml": {}},
    }
})
def get_card(game: str, uid: int):
    if game not in support_game:
        return {"msg": "game not support"}
    try:
        player_info = get_genshin(uid)
    except Exception as e:
        return {"msg": f"get player info error: {e}"}
    if not player_info:
        return {"msg": "player not found"}
    generate_card(game, player_info)
    return FileResponse(f'./cache/card/{game}_{uid}.svg', media_type='image/svg+xml')