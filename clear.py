from discord.ext import commands
import discord

async def clear_messages(ctx: commands.Context, amount: int = 10):
    """
    Borra una cantidad específica de mensajes en el canal actual.
    :param ctx: Contexto del comando.
    :param amount: Número de mensajes a borrar (por defecto 10).
    """
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("🚫 No tienes permisos para borrar mensajes.")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            description=f"🧹 {len(deleted)} mensajes eliminados.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=4)
    except Exception as e:
        await ctx.send("⚠️ Ocurrió un error al intentar borrar los mensajes.", delete_after=5)
        print(f"⚠️ Error al borrar mensajes: {e}")

def setup_commands(bot: commands.Bot):
    @bot.command(name="clear")
    async def clear(ctx, amount: int = 10):
        await clear_messages(ctx, amount)
