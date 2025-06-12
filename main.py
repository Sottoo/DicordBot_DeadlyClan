import discord
from discord.ext import commands
from commands import setup_commands
from events import setup_events
from clear import setup_commands as setup_clear_commands
from avisos import setup_avisos
from spam import setup_spam_commands, detect_spam
from antilinks import setup_antilinks, check_links
from rewards import setup_rewards_commands
from Trivia import trivia
from sondeos import sondeo
from cringe import setup_cringe_commands
from bromalocal import setup_bromalocal_commands
from help import setup as setup_help_commands
from musica import setup as setup_music_commands
import os
import asyncio
import threading
from flask import Flask

# Configuración de intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

# Instancia del bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Registrar comandos y eventos
setup_commands(bot)
setup_events(bot)
setup_clear_commands(bot)
setup_avisos(bot)
setup_spam_commands(bot)
setup_antilinks(bot)
setup_rewards_commands(bot)
setup_cringe_commands(bot)
setup_bromalocal_commands(bot)
setup_help_commands(bot)
bot.add_command(trivia)
bot.add_command(sondeo)

# Evento on_ready
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Moderando Deadly Clan"))
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    print("Conectado a los siguientes servidores:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

# Evento on_message
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await detect_spam(message)
    await check_links(message)

    from rewards import add_xp
    await add_xp(message.author, 1, message.channel)

    await bot.process_commands(message)

# Registra los comandos de recompensas
setup_rewards_commands(bot)

# Flask app para mantener activo
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo."

def run_webserver():
    app.run(host="0.0.0.0", port=8080)

async def autosave_xp():
    await bot.wait_until_ready()
    while not bot.is_closed():
        save_user_xp()
        await asyncio.sleep(60)

@bot.event
async def on_ready():
    print(f"{bot.user} listo. Conectado a {len(bot.guilds)} servidores.")
    bot.loop.create_task(autosave_xp())

@bot.event
async def on_disconnect():
    print("🔌 Bot desconectado: guardando XP...")
    save_user_xp()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await add_xp(message.author, 1, message.channel)
    await bot.process_commands(message)

async def start_bot():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("🔴 Falta DISCORD_TOKEN")
    bot.loop.create_task(autosave_xp())
    await bot.start(token)

if __name__ == "__main__":
    threading.Thread(target=run_webserver).start()
    asyncio.run(start_bot())
