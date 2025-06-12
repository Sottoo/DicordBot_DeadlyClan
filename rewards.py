import discord
from discord.ext import commands
from collections import defaultdict
import json
import os

# Archivo donde se guardan los datos
DATA_FILE = "user_xp.json"

# Diccionario de XP de usuarios
user_xp = defaultdict(int)

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

# Cargar datos
def load_user_xp():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                for user_id, xp in data.items():
                    user_xp[int(user_id)] = xp
        except Exception as e:
            print(f"⚠️ Error al cargar XP: {e}")

# Guardar datos
def save_user_xp():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(dict(user_xp), file, ensure_ascii=False, indent=4)
        print("✅ XP guardado.")
    except Exception as e:
        print(f"⚠️ Error al guardar XP: {e}")

# Cargar al iniciar
load_user_xp()

# Sumar XP a un usuario
async def add_xp(member: discord.Member, xp: int, channel: discord.TextChannel):
    user_id = member.id
    previous_xp = user_xp[user_id]
    user_xp[user_id] += xp
    print(f"[XP] {member.name}: {previous_xp} → {user_xp[user_id]}")
    save_user_xp()

    for rank in reversed(RANKS):
        if user_xp[user_id] >= rank["xp_required"] > previous_xp:
            await handle_rank_up(member, rank, channel)
            break

# Manejar subida de rango
async def handle_rank_up(member: discord.Member, rank: dict, channel: discord.TextChannel):
    embed = discord.Embed(
        title="🎉 ¡Has subido de rango!",
        description=f"{member.mention}, ahora eres **{rank['name']}**.",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="Rango", value=rank["name"], inline=True)

    role = discord.utils.get(member.guild.roles, id=rank["reward"])
    if role:
        if role not in member.roles:
            await member.add_roles(role, reason="Subida de rango")
        embed.add_field(name="Recompensa", value=f"Rol otorgado: {role.mention}", inline=True)
    else:
        embed.add_field(name="Recompensa", value="No se encontró el rol 😢", inline=True)

    await channel.send(embed=embed)

# Comandos del sistema de recompensas
def setup_rewards_commands(bot: commands.Bot):
    @bot.command(name="rank")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def check_rank(ctx):
        sorted_users = sorted(user_xp.items(), key=lambda item: item[1], reverse=True)
        lines = []
        for i, (uid, xp) in enumerate(sorted_users[:10], start=1):
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"Usuario ({uid})"
            emoji = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else "🏅"
            lines.append(f"{emoji} **#{i}** {name} - **{xp} XP**")

        # Posición del usuario si no está en el top 10
        user_pos = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == ctx.author.id), None)
        if user_pos and user_pos > 10:
            lines.append(f"\n🔽 Tu posición: #{user_pos} - **{user_xp[ctx.author.id]} XP**")

        embed = discord.Embed(title="🏆 Ranking de XP", description="\n".join(lines), color=discord.Color.purple())
        await ctx.send(embed=embed)

    @bot.command(name="progreso")
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def progreso(ctx, member: discord.Member = None):
        member = member or ctx.author
        xp = user_xp.get(member.id, 0)
        next_rank = next((r for r in RANKS if xp < r["xp_required"]), None)

        if next_rank:
            current_rank = next((r["name"] for r in reversed(RANKS) if xp >= r["xp_required"]), "Sin rango")
            needed_xp = next_rank["xp_required"] - xp
            progress = xp / next_rank["xp_required"]
            bar_length = 30
            filled = int(progress * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            embed = discord.Embed(title="📈 Tu progreso", color=discord.Color.blue())
            embed.add_field(name="Rango actual", value=current_rank, inline=True)
            embed.add_field(name="Siguiente rango", value=next_rank["name"], inline=True)
            embed.add_field(name="XP actual", value=f"{xp} / {next_rank['xp_required']}", inline=True)
            embed.add_field(name="Faltan", value=f"{needed_xp} XP", inline=True)
            embed.add_field(name="Progreso", value=f"`[{bar}] {progress*100:.2f}%`", inline=False)
        else:
            embed = discord.Embed(
                title="🎉 Rango máximo alcanzado",
                description=f"{member.mention} ya tiene el rango **{RANKS[-1]['name']}**.",
                color=discord.Color.green()
            )

        await ctx.send(embed=embed)

    # Manejo de errores de cooldown
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after)
            h, m = divmod(seconds, 3600)
            m, s = divmod(m, 60)
            embed = discord.Embed(
                title="⏱️ Cooldown",
                description=f"Espera {h}h {m}m {s}s para usar `{ctx.command.name}` de nuevo.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            raise error
