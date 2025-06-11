import discord
from discord.ext import commands

@commands.command(name="ayuda")  # Renombrar el comando a "ayuda"
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Comandos Disponibles",
        description="Aquí tienes una lista de los comandos públicos clasificados por secciones:",
        color=discord.Color.blue()
    )

    # Sección: Encuestas y Juegos
    embed.add_field(
        name="🎮 Encuestas y Juegos",
        value=(
            "**!sondeo** - Inicia un sondeo con preguntas predefinidas.\n"
            "**!trivia** - Participa en una trivia divertida.\n"
            "**!cringe** - Mide el nivel de cringe de un usuario."
            "**!pene** - Mide el nivel de gusto de un usuario."
        ),
        inline=False
    )

    # Sección: Progreso y Rangos
    embed.add_field(
        name="📈 Progreso y Rangos",
        value=(
            "**!progreso** - Muestra tu progreso actual en el servidor.\n"
            "**!rank** - Consulta tu posición en el ranking del servidor."
        ),
        inline=False
    )

    embed.set_footer(text="Usa los comandos con el prefijo '!'.")
    await ctx.send(embed=embed)

def setup(bot):
    bot.add_command(help_command)
