import discord
from discord.ext import commands
from commands import setup_commands
from events import setup_events
from clear import setup_commands as setup_clear_commands
from avisos import setup_avisos
from spam import setup_spam_commands, detect_spam
from antilinks import setup_antilinks, check_links
from rewards import setup_rewards_commands, add_xp
from Trivia import trivia
from sondeos import sondeo
from cringe import setup_cringe_commands
from bromalocal import setup_bromalocal_commands
from help import setup as setup_help_commands
import threading
import os
import asyncio
import time
from flask import Flask


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents
)

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


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(
            name="Moderando Deadly Clan"
        )
    )
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    print("Conectado a los siguientes servidores:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    # Ignorar mensajes de bots
    if message.author.bot:
        return

    # Llamar a las funciones específicas de cada módulo
    await detect_spam(message)  # Desde spam.py
    await check_links(message)  # Desde antilinks.py

    # Agregar XP por mensaje
    from rewards import add_xp  # Importar aquí para evitar conflictos circulares
    await add_xp(message.author, 1, message.channel)  # 1 XP por mensaje

    # Procesar comandos después de manejar el mensaje
    await bot.process_commands(message)


app = Flask(__name__)

@app.route("/")
def home():
    return "El bot está activo y funcionando correctamente."

def run_webserver():
    app.run(host="0.0.0.0", port=8080)

# Iniciar el bot y el servidor web
def start_bot():
    try:
        # Leer el token desde las variables de entorno
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("⚠️ Variable de entorno 'DISCORD_TOKEN' no encontrada. Por favor, configúrala correctamente.")

        bot.run(token)  # Discord.py maneja automáticamente las reconexiones
    except discord.errors.HTTPException as e:
        print(f"⚠️ Error de conexión: {e}. Verifica el token y los permisos del bot.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")

if __name__ == "__main__":
    # Ejecutar el servidor web en un hilo separado
    threading.Thread(target=run_webserver).start()

    # Iniciar el bot
    start_bot()
