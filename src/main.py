from infi.systray import SysTrayIcon
from discord.ext import tasks
import discord

from platform import system
from traceback import format_exc
from utility import log
import os
import json
import commands

with open("config.json", encoding="utf-8") as f:
	config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
client = discord.Client(intents=intents)

commands.config = config
commands.client = client

@tasks.loop(seconds=360)
async def schedule_watcher():
    try:
        await commands.cmd_force_schedule_update(None, None)
    except Exception:
        log(f"[EXCEPTION] schedule_watcher: {format_exc()}")

@client.event
async def on_message(message):
    try:
        if message.content.startswith(config["prefix"]):
            await commands.handle_admin_commands(message)
            await commands.handle_user_commands(message)
    except Exception:
        log(f"[EXCEPTION] on_message: {format_exc()}")

@client.event
async def on_ready():
    schedule_watcher.start()

    if system() == "Windows":
        def on_quit_callback(systray):
            os._exit(0)
        
        systray = SysTrayIcon(None, "KGB", None, on_quit=on_quit_callback)
        systray.start()

    log(f"[INFO] Logged in as {client.user} (ID: {client.user.id})")     

if __name__ == "__main__":
	client.run(config["token"])