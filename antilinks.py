import discord
from discord.ext import commands
import re

# Expresión regular para detectar enlaces
URL_REGEX = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+)",
    re.IGNORECASE
)

# Puedes personalizar aquí patrones sospechosos
SUSPECT_PATTERNS = [
    r"discord\.gift",  # Detecta cualquier subdominio o combinación con discord.gift
    r"discord[-_.]?airdrop",  # Detecta combinaciones como discord-airdrop o discord_airdrop
    r"nitro[-_.]?",  # Detecta combinaciones como nitro-, nitro_, etc.
    r"free[-_.]?nitro",  # Detecta combinaciones como free-nitro o free_nitro
    r"steamgift",  # Detecta cualquier mención de steamgift
    r"steamcommunity",  # Detecta cualquier mención de steamcommunity
    r"bit\.ly"  # Detecta cualquier enlace de bit.ly
]

# Ajustar la lógica para detectar combinaciones sospechosas
async def check_links(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower()
    urls = URL_REGEX.findall(content)
    if not urls:
        return

    # Si el usuario tiene permisos de administrador, ignora
    if hasattr(message.author, "guild_permissions") and message.author.guild_permissions.administrator:
        return

    # Buscar patrones sospechosos en las URLs
    for url in urls:
        for pattern in SUSPECT_PATTERNS:
            if re.search(pattern, url):  # Detectar si el patrón coincide con la URL
                try:
                    await message.delete()
                    embed = discord.Embed(
                        description=f"🚫 {message.author.mention}, tu mensaje fue eliminado por contener un enlace sospechoso.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed, delete_after=8)
                    print(f"[ANTILINKS] Mensaje de {message.author} eliminado: {url}")
                except Exception as e:
                    print(f"[ANTILINKS] Error al eliminar mensaje: {e}")
                return

def setup_antilinks(bot):
    # Elimina el evento on_message aquí
    pass
