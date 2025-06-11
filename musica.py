import discord
from discord.ext import commands
import youtube_dl
import asyncio

# Configuración de youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ""
ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
}
ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @commands.command(name="join")
    async def join(self, ctx):
        """Unirse al canal de voz del usuario."""
        try:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                self.voice_client = await channel.connect()
                await ctx.send(f"✅ Me he unido al canal de voz: {channel.name}")
            else:
                await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
        except RuntimeError as e:
            if "PyNaCl library needed" in str(e):
                await ctx.send("⚠️ Error: La biblioteca PyNaCl no está instalada. Por favor, instálala usando `pip install pynacl`.")
            else:
                await ctx.send(f"⚠️ Error inesperado: {e}")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Salir del canal de voz."""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            await ctx.send("✅ He salido del canal de voz.")
        else:
            await ctx.send("❌ No estoy en ningún canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, *, url):
        """Reproducir música desde una URL de YouTube."""
        if not self.voice_client:
            await ctx.send("❌ Primero usa el comando `!join` para que me una a un canal de voz.")
            return

        try:
            await ctx.send("🔍 Buscando la canción...")
            info = ytdl.extract_info(url, download=False)
            url2 = info['url']
            title = info.get('title', 'Audio desconocido')

            self.voice_client.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
            await ctx.send(f"🎶 Reproduciendo: **{title}**")
        except Exception as e:
            await ctx.send(f"⚠️ Error al reproducir la música: {e}")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Detener la música."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("⏹️ Música detenida.")
        else:
            await ctx.send("❌ No hay música reproduciéndose actualmente.")

async def setup(bot):
    await bot.add_cog(Music(bot))  # Usar await para agregar el cog correctamente
