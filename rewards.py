import discord
from discord.ext import commands
import json
import os
import asyncpg

# URL de conexión de Railway (usa tu variable de entorno o ponla aquí directamente)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:uiaaDOthTpvfNYuaIHQCsVlxfeIdoqHt@yamabiko.proxy.rlwy.net:45928/railway")

db_pool = None  # Pool global

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_xp (
                user_id BIGINT PRIMARY KEY,
                xp INTEGER NOT NULL
            );
        """)

async def get_xp(user_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT xp FROM user_xp WHERE user_id = $1", user_id)
        return row["xp"] if row else 0

async def set_xp(user_id, xp):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_xp (user_id, xp) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET xp = EXCLUDED.xp
        """, user_id, xp)

async def top_xp(limit=10):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, xp FROM user_xp ORDER BY xp DESC LIMIT $1", limit)
        return [(r["user_id"], r["xp"]) for r in rows]

# RANGOS Y RECOMPENSAS
RANKS = [
    {"name": "Classic", "xp_required": 100, "reward": 1381559103918178364},
    {"name": "Bronze", "xp_required": 200, "reward": 1148104130112659616},
    {"name": "Silver", "xp_required": 400, "reward": 1148104263939256340},
    {"name": "Gold", "xp_required": 600, "reward": 1148104373932328960},
    {"name": "Platinum", "xp_required": 1000, "reward": 1148104557550039040},
    {"name": "Diamond", "xp_required": 1500, "reward": 1148104661703837787},
    {"name": "Ruby", "xp_required": 2500, "reward": 1148104780375187506},
    {"name": "Master", "xp_required": 5000, "reward": 1148104882874255410},
    {"name": "Elite", "xp_required": 10000, "reward": 1148105039050170429},
    {"name": "Legend", "xp_required": 15000, "reward": 1148105224451754095},
]

# Sumar XP a un usuario
async def add_xp(member: discord.Member, xp: int, channel: discord.TextChannel):
    user_id = member.id
    previous_xp = await get_xp(user_id)
    new_xp = previous_xp + xp
    await set_xp(user_id, new_xp)
    print(f"[XP] {member.name}: {previous_xp} → {new_xp}")

    for rank in reversed(RANKS):
        if new_xp >= rank["xp_required"] > previous_xp:
            await handle_rank_up(member, rank, channel)
            break

# Manejar subida de rango
async def handle_rank_up(member: discord.Member, rank: dict, channel: discord.TextChannel):
    embed = discord.Embed(
        title="✨ ¡Ascenso de Rango!",
        description=f"🎉 Felicidades {member.mention}, has alcanzado el rango **{rank['name']}**.",
        color=discord.Color.from_rgb(255, 215, 0)  # Dorado brillante
    )
    embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
    embed.add_field(name="🏅 Nuevo Rango", value=f"**{rank['name']}**", inline=True)

    role = discord.utils.get(member.guild.roles, id=rank["reward"])
    if role:
        if role not in member.roles:
            await member.add_roles(role, reason="Subida de rango")
        embed.add_field(name="🎁 Recompensa", value=f"Rol otorgado: {role.mention}", inline=True)
    else:
        embed.add_field(name="🎁 Recompensa", value="No se encontró el rol 😢", inline=True)

    embed.set_footer(text="¡Sigue participando para alcanzar el siguiente rango!", icon_url="https://cdn-icons-png.flaticon.com/512/1828/1828884.png")
    await channel.send(embed=embed)

# Comandos del sistema de recompensas
def setup_rewards_commands(bot: commands.Bot):
    @bot.command(name="rank")
    async def check_rank(ctx):
        top = await top_xp(10)
        lines = []
        for i, (uid, xp) in enumerate(top, start=1):
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"Usuario ({uid})"
            emoji = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else "🏅"
            lines.append(f"{emoji} **#{i}** {name} — **{xp} XP**")

        user_xp_val = await get_xp(ctx.author.id)
        # Para posición real, consulta todos los usuarios (puedes optimizar esto)
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM user_xp ORDER BY xp DESC")
            user_pos = next((i+1 for i, r in enumerate(rows) if r["user_id"] == ctx.author.id), None)
        if user_pos and user_pos > 10:
            lines.append(f"\n🔽 Tu posición: **#{user_pos}** — **{user_xp_val} XP**")

        embed = discord.Embed(
            title="🏆 Ranking de XP",
            description="\n".join(lines),
            color=discord.Color.from_rgb(138, 43, 226)  # Morado vibrante
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="¡Compite y sube en el ranking!", icon_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
        await ctx.send(embed=embed)

    @bot.command(name="progreso")
    async def progreso(ctx, member: discord.Member = None):
        member = member or ctx.author
        xp = await get_xp(member.id)
        next_rank = next((r for r in RANKS if xp < r["xp_required"]), None)

        if next_rank:
            current_rank = next((r["name"] for r in reversed(RANKS) if xp >= r["xp_required"]), "Sin rango")
            needed_xp = next_rank["xp_required"] - xp
            progress = xp / next_rank["xp_required"]
            bar_length = 30
            filled = int(progress * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            embed = discord.Embed(
                title="📈 Progreso de Rango",
                color=discord.Color.from_rgb(30, 144, 255)  # Azul profesional
            )
            embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
            embed.add_field(name="🏅 Rango actual", value=current_rank, inline=True)
            embed.add_field(name="🎯 Siguiente rango", value=next_rank["name"], inline=True)
            embed.add_field(name="🔢 XP actual", value=f"{xp} / {next_rank['xp_required']}", inline=True)
            embed.add_field(name="⏳ Faltan", value=f"{needed_xp} XP", inline=True)
            embed.add_field(name="📊 Progreso", value=f"`[{bar}] {progress*100:.2f}%`", inline=False)
            embed.set_footer(text="¡Sigue participando para subir de rango!", icon_url="https://cdn-icons-png.flaticon.com/512/1828/1828884.png")
        else:
            embed = discord.Embed(
                title="🏅 ¡Rango Máximo Alcanzado!",
                description=f"🎉 {member.mention} ya tiene el rango **{RANKS[-1]['name']}**.",
                color=discord.Color.from_rgb(50, 205, 50)  # Verde éxito
            )
            embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
            embed.set_footer(text="¡Eres una leyenda!", icon_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")

        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await init_db()
        print(f"Bot listo como {bot.user}")

    # Manejo de errores de cooldown
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after)
            h, m = divmod(seconds, 3600)
            m, s = divmod(m, 60)
            embed = discord.Embed(
                title="⏱️ ¡Espera un poco!",
                description=f"Debes esperar **{h}h {m}m {s}s** para usar `{ctx.command.name}` de nuevo.",
                color=discord.Color.from_rgb(255, 140, 0)  # Naranja llamativo
            )
            embed.set_footer(text="Evita el spam para mantener el sistema justo.", icon_url="https://cdn-icons-png.flaticon.com/512/565/565547.png")
            await ctx.send(embed=embed, delete_after=10)
        else:
            raise error
