from discord.ext import commands
import discord
from datetime import datetime
import pytz

def setup_avisos(bot):
    @bot.command(name="anuncio")
    @commands.has_permissions(administrator=True)
    async def anuncio(ctx, *, mensaje: str):
        canal_anuncios = ctx.guild.get_channel(1381159857524051990)
        if canal_anuncios:
            # Permitir título opcional usando el formato: !anuncio Título | Mensaje
            if "|" in mensaje:
                titulo, contenido = mensaje.split("|", 1)
                titulo = titulo.strip()
                contenido = contenido.strip()
            else:
                titulo = "📢 Anuncio Importante"
                contenido = mensaje.strip()

            # Hora de México/Guadalajara
            tz = pytz.timezone("America/Mexico_City")
            hora_mexico = datetime.now(tz)

            embed = discord.Embed(
                title=titulo,
                description=contenido,
                color=discord.Color.gold(),
                timestamp=hora_mexico
            )
            embed.set_footer(text=f"Anunciado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            await canal_anuncios.send(embed=embed)
            await ctx.send("✅ Anuncio enviado con éxito.")
        else:
            await ctx.send("❌ No se encontró el canal de anuncios.")