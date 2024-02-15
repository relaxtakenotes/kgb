from discord.ext import tasks
import discord

from traceback import format_exc
import json
import commands

with open("config.json") as f:
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
        log(f"schedule_watcher: {format_exc()}")

@client.event
async def on_message(message):
    try:
        if message.content.startswith(config["prefix"]):
            await commands.handle_admin_commands(message)
            await commands.handle_user_commands(message)
    except Exception:
        log(f"on_message: {format_exc()}")

@client.event
async def on_ready():
    schedule_watcher.start()

    print(f"Logged in as {client.user} (ID: {client.user.id})")     

if __name__ == "__main__":
	client.run(config["token"])