import os
import uvicorn
import bot_config as bot_config
from fastapi import FastAPI, Request
from bot_class import ControlBot


# %%

app = FastAPI()
bot = ControlBot(BOT_URL=bot_config.BOT_URL,
                 CODES_LIMIT=bot_config.CODES_LIMIT,
                 INS_URL=bot_config.INS_URL)


# %%

@app.post('/')
async def webhook_handler(request: Request):
    update = await request.json()
    bot.handle_updates(update)
    return {'result': 'OK'}


# %%

PORT = int(os.environ.get('PORT', 5000))
# HOOK = 'https://1f679d45a60f.ngrok.io'  # for local development
HOOK = 'https://sleepy-woodland-05300.herokuapp.com/'

if __name__ == '__main__':
    bot.setup()
    bot.get_url(bot_config.BOT_URL +
                'setWebHook?url={}'
                .format(HOOK))
    uvicorn.run('bot_script:app', host='0.0.0.0', port=PORT)
