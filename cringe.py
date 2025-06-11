import discord
from discord.ext import commands
import random

def setup_cringe_commands(bot):
    @bot.command(name="cringe")
    async def cringe(ctx, member: discord.Member):
        cringe_percentage = random.randint(0, 100)
        if cringe_percentage < 30:
            level = "✨ Apenas da cringe"
            color = discord.Color.green()
        elif cringe_percentage < 70:
            level = "😬 Moderadamente da cringe"
            color = discord.Color.orange()
        else:
            level = "💀 Absolutamente da cringe"
            color = discord.Color.red()

        embed = discord.Embed(
            title="📉 Cringeómetro",
            description=(
                f"{member.mention} tiene un nivel de cringe de **{cringe_percentage}%**.\n\n"
                f"**Nivel:** {level}"
            ),
            color=color
        )
        embed.set_footer(text="¡El cringeómetro nunca falla!")
        embed.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/actions-alphabet-c-set-23-of-25/246/actions-C-23-3-512.png")  # Cambia la URL por una imagen adecuada
        await ctx.send(embed=embed)
