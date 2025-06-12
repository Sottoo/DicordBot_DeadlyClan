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

# ID del canal de backup (pon aquí el ID real de tu canal)
BACKUP_CHANNEL_ID = 1382537437326213211 # <-- Cambia esto por el canal de backup

xp_restaurado = False  # Bandera para saber si la XP fue restaurada correctamente

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

# Guardar datos en canal de Discord
async def save_user_xp_discord(bot):
    channel = bot.get_channel(BACKUP_CHANNEL_ID)
    if not channel:
        print("⚠️ No se encontró el canal de backup para XP.")
        return
    data = json.dumps(dict(user_xp), ensure_ascii=False, indent=4)
    async for msg in channel.history(limit=10):
        if msg.author == bot.user and msg.content.startswith("XP_BACKUP:"):
            await msg.edit(content=f"XP_BACKUP:\n```json\n{data}\n```")
            print("✅ XP guardado en Discord (editado).")
            return
    await channel.send(f"XP_BACKUP:\n```json\n{data}\n```")
    print("✅ XP guardado en Discord (nuevo mensaje).")

# Cargar datos desde canal de Discord
async def load_user_xp_discord(bot):
    global xp_restaurado
    channel = bot.get_channel(BACKUP_CHANNEL_ID)
    if not channel:
        print("⚠️ No se encontró el canal de backup para XP.")
        return
    async for msg in channel.history(limit=20):
        if msg.content.startswith("XP_BACKUP:"):
            try:
                content = msg.content
                json_str = content.split("```json")[1].split("```")[0]
                data = json.loads(json_str)
                for user_id, xp in data.items():
                    user_xp[int(user_id)] = xp
                xp_restaurado = True
                print(f"✅ XP restaurado desde Discord (mensaje ID: {msg.id}).")
            except Exception as e:
                print(f"⚠️ Error al cargar XP desde Discord: {e}")
            return
    print("⚠️ No se encontró ningún respaldo XP_BACKUP en el canal de backup.")

# Cargar al iniciar
load_user_xp()

# Sumar XP a un usuario
async def add_xp(member: discord.Member, xp: int, channel: discord.TextChannel):
    user_id = member.id
    previous_xp = user_xp[user_id]
    user_xp[user_id] += xp
    print(f"[XP] {member.name}: {previous_xp} → {user_xp[user_id]}")
    save_user_xp()
    # Guardar automáticamente en Discord solo si la XP fue restaurada o ya existía
    bot = channel.guild._state._get_client()
    if bot and xp_restaurado:
        await save_user_xp_discord(bot)

    for rank in reversed(RANKS):
        if user_xp[user_id] >= rank["xp_required"] > previous_xp:
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
        sorted_users = sorted(user_xp.items(), key=lambda item: item[1], reverse=True)
        lines = []
        for i, (uid, xp) in enumerate(sorted_users[:10], start=1):
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"Usuario ({uid})"
            emoji = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else "🏅"
            lines.append(f"{emoji} **#{i}** {name} — **{xp} XP**")

        user_pos = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == ctx.author.id), None)
        if user_pos and user_pos > 10:
            lines.append(f"\n🔽 Tu posición: **#{user_pos}** — **{user_xp[ctx.author.id]} XP**")

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
        xp = user_xp.get(member.id, 0)
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

    @bot.command(name="backup_xp")
    @commands.has_permissions(administrator=True)
    async def backup_xp(ctx):
        await save_user_xp_discord(ctx.bot)
        await ctx.send("XP respaldado en el canal de backup.")

    @bot.command(name="restore_xp")
    @commands.has_permissions(administrator=True)
    async def restore_xp(ctx):
        await load_user_xp_discord(ctx.bot)
        save_user_xp()
        await ctx.send("XP restaurado desde el canal de backup.")

    @bot.event
    async def on_ready():
        global xp_restaurado
        # Si no existe el archivo local, intenta restaurar desde Discord
        if not os.path.exists(DATA_FILE):
            await load_user_xp_discord(bot)
            save_user_xp()
        else:
            xp_restaurado = True  # Ya existía localmente, se puede guardar en Discord
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
