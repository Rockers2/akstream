import os, sys, glob, pytz, asyncio, logging, importlib
from pathlib import Path
from pyrogram import idle
from aiohttp import web
import aiohttp  # for self-ping

# Dont Remove My Credit @AV_BOTz_UPDATE
# This Repo Is By @BOT_OWNER26
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from info import *
from typing import Union, Optional, AsyncGenerator
from Script import script
from datetime import date, datetime
from web import web_server, check_expired_premium
from web.server import Webavbot
from utils import temp, ping_server
from web.server.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
Webavbot.start()
loop = asyncio.get_event_loop()

# ---------------- Self Ping Function ----------------
async def self_ping():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://faithful-jodi-knmlpro2-006d3b71.koyeb.app/ping") as resp:
                    print(f"Self-ping status: {resp.status}")
        except Exception as e:
            print(f"Ping error: {e}")
        await asyncio.sleep(300)  # every 5 minutes
# -----------------------------------------------------

async def start():
    print('\n')
    print('Initializing Your Bot')
    bot_info = await Webavbot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Imported => " + plugin_name)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    me = await Webavbot.get_me()
    temp.BOT = Webavbot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    Webavbot.loop.create_task(check_expired_premium(Webavbot))

    await Webavbot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    await Webavbot.send_message(chat_id=ADMINS[0], text='<b>ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ !!</b>')
    await Webavbot.send_message(chat_id=SUPPORT_GROUP, text=f"<b>{me.mention} ʀᴇsᴛᴀʀᴛᴇᴅ 🤖</b>")

    # --- Add Keep-Alive Ping Route ---
    app = await web_server()
    async def ping(request):
        return web.Response(text="Pong")
    app.router.add_get('/ping', ping)
    # ---------------------------------

    runner = web.AppRunner(app)
    await runner.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(runner, bind_address, PORT).start()

    # Start self-ping in background
    Webavbot.loop.create_task(self_ping())

    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('----------------------- Service Stopped -----------------------')
