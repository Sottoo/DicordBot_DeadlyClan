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

# Servidor web Flask para mantener el bot activo (opcional en servicios como Replit)
app = Flask(__name__)

@app.route("/")
def home():
    return "El bot está activo y funcionando correctamente."

def run_webserver():
    app.run(host="0.0.0.0", port=8080)

# Función principal para iniciar el bot
async def start_bot():
    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("⚠️ Variable de entorno 'DISCORD_TOKEN' no encontrada.")

        await setup_music_commands(bot)  # Registrar comandos de música
        await bot.start(token)

    except discord.errors.HTTPException as e:
        print(f"⚠️ Error de conexión: {e}")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_webserver).start()
    asyncio.run(start_bot())
