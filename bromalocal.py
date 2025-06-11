import discord
from discord.ext import commands
import random

def setup_bromalocal_commands(bot):
    @bot.command(name="pene")
    async def bromalocal(ctx, member: discord.Member):
        cringe_percentage = random.randint(0, 100)
        if cringe_percentage < 30:
            level = "✨ No le gusta tanto el pene"
            color = discord.Color.green()
        elif cringe_percentage < 70:
            level = "😬 Medio medio"
            color = discord.Color.orange()
        else:
            level = "💀 Absolutamente le gusta el pene"
            color = discord.Color.red()

        embed = discord.Embed(
            title="📉 Penenómetro",
            description=(
                f"{member.mention} tiene un nivel de gusto por la rama de **{cringe_percentage}%**.\n\n"
                f"**Nivel:** {level}"
            ),
            color=color
        )
        embed.set_footer(text="¡El penenometro nunca falla!")
        embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/previews/007/126/739/original/question-mark-icon-free-vector.jpg")
        await ctx.send(embed=embed)
