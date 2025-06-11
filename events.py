import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from bienvenida import send_welcome_message
from spam import detect_spam

def setup_events(bot: commands.Bot):
    @bot.event
    async def on_ready():
        print(f'✅ Bot conectado como {bot.user}')
        print("🔍 Servidores conectados:")
        for guild in bot.guilds:
            print(f"- {guild.name} (ID: {guild.id})")

    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.emoji.name != "✅":
            return

        print(f"🔄 Reacción detectada de usuario ID {payload.user_id} en mensaje ID {payload.message_id}")

        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            print("⚠️ Servidor no encontrado.")
            return

        try:
            member = guild.get_member(payload.user_id)
            if member is None:
                member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print(f"⚠️ No se pudo obtener el miembro: {e}")
            return

        if member.bot:
            print("🤖 El usuario es un bot. Ignorando.")
            return

        role_id = 1381182782105190400  # ⚠️ Asegúrate de que este ID sea correcto
        role = guild.get_role(role_id)

        if role is None:
            print(f"⚠️ Rol con ID {role_id} no encontrado.")
            return

        try:
            await member.add_roles(role, reason="Aceptó las reglas")
            print(f"✅ Rol '{role.name}' asignado a {member.name}")
        except discord.Forbidden:
            print("🚫 Permisos insuficientes para asignar el rol.")
        except Exception as e:
            print(f"⚠️ Error inesperado: {e}")

    @bot.event
    async def on_raw_reaction_remove(payload):
        if payload.emoji.name != "✅":
            return

        print(f"🔄 Reacción eliminada por usuario ID {payload.user_id} en mensaje ID {payload.message_id}")

        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            print("⚠️ Servidor no encontrado.")
            return

        try:
            member = guild.get_member(payload.user_id)
            if member is None:
                member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print(f"⚠️ No se pudo obtener el miembro: {e}")
            return

        if member.bot:
            print("🤖 El usuario es un bot. Ignorando.")
            return

        role_id = 1381182782105190400  # ⚠️ Asegúrate de que este ID sea correcto
        role = guild.get_role(role_id)

        if role is None:
            print(f"⚠️ Rol con ID {role_id} no encontrado.")
            return

        try:
            await member.remove_roles(role, reason="Quitó la reacción de aceptación")
            print(f"❌ Rol '{role.name}' removido de {member.name}")
        except discord.Forbidden:
            print("🚫 Permisos insuficientes para remover el rol.")
        except Exception as e:
            print(f"⚠️ Error inesperado: {e}")

    @bot.event
    async def on_member_join(member):
        # Llamar a la función de bienvenida renombrada
        await send_welcome_message(member)

