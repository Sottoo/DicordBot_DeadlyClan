import discord
from discord.ext import commands
from collections import defaultdict
import json
import asyncio 
import os

# Diccionario para rastrear XP de los usuarios
user_xp = defaultdict(int)  # {user_id: xp}

# Ruta del archivo donde se guardarán los datos
DATA_FILE = "user_xp.json"

# Función para cargar los datos desde el archivo
def load_user_xp():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                for user_id, xp in data.items():
                    user_xp[int(user_id)] = xp
        except Exception as e:
            print(f"⚠️ Error al cargar los datos: {e}")

# Función para guardar los datos en el archivo
def save_user_xp():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(user_xp, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Error al guardar los datos: {e}")

# Cargar los datos al iniciar el bot
load_user_xp()

# Configuración de rangos y recompensas
RANKS = [
    {"name": "Classic", "xp_required": 100, "reward": 1381559103918178364}, 
    {"name": "Ghost", "xp_required": 300, "reward": 1381559234734456852},  
    {"name": "Sheriff", "xp_required": 500, "reward": 1381560029924298905},
    {"name": "Stinger", "xp_required": 700, "reward": 1381887228371800204},
    {"name": "Spectre", "xp_required": 1000, "reward": 1381887664973676594},
    {"name": "Bulldog", "xp_required": 1500, "reward": 1381887795865587712},
    {"name": "Phantom", "xp_required": 2000, "reward": 1381888008759804004},
    {"name": "Vandal", "xp_required": 3000, "reward": 1381888156969730109},
    {"name": "Rey Demonio", "xp_required": 5000, "reward": 1381892210978455592},
]

async def add_xp(member: discord.Member, xp: int, channel: discord.TextChannel):
    user_id = member.id
    previous_xp = user_xp[user_id]
    user_xp[user_id] += xp

    # Guardar los datos después de actualizar el XP
    save_user_xp()

    # Verificar si el usuario sube de rango
    current_xp = user_xp[user_id]
    for rank in reversed(RANKS):
        if current_xp >= rank["xp_required"] and previous_xp < rank["xp_required"]:
            await handle_rank_up(member, rank, channel)
            break

async def handle_rank_up(member: discord.Member, rank: dict, channel: discord.TextChannel):
    # Mensaje de rango alcanzado
    embed = discord.Embed(
        title="🎉 ¡Felicidades por tu nuevo rango!",
        description=(
            f"✨ {member.mention}, has alcanzado el rango **{rank['name']}**.\n\n"
            f"🎖️ ¡Sigue participando para alcanzar el siguiente rango y obtener más recompensas!"
        ),
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(
        name="🎯 Rango Alcanzado",
        value=f"**{rank['name']}**",
        inline=True
    )
    if rank["reward"]:
        embed.add_field(
            name="🎁 Recompensa",
            value="Se te ha asignado un nuevo rol en el servidor.",
            inline=True
        )
    else:
        embed.add_field(
            name="🎁 Recompensa",
            value="No hay recompensa específica para este rango.",
            inline=True
        )
    embed.set_footer(
        text="¡Gracias por ser parte de Deadly Clan!",
        icon_url="https://cdn-icons-png.flaticon.com/512/847/847969.png"
    )
    await channel.send(embed=embed)

    # Asignar el rol específico si tiene un ID de recompensa
    if rank["reward"]:
        specific_role = discord.utils.get(member.guild.roles, id=rank["reward"])
        if specific_role:
            if specific_role not in member.roles:  # Verificar si el usuario ya tiene el rol
                await member.add_roles(specific_role, reason=f"Recompensa por alcanzar el rango {rank['name']}")
        else:
            await channel.send(f"🚫 No se encontró el rol específico '{rank['name']}'.", delete_after=10)

# Comando para verificar el XP actual
def setup_rewards_commands(bot: commands.Bot):
    @bot.command(name="rank")
    @commands.cooldown(1, 3600, commands.BucketType.user)  # 1 uso cada 3600 segundos (1 hora) por usuario
    async def check_rank(ctx):
        # Ordenar usuarios por XP en orden descendente
        sorted_users = sorted(user_xp.items(), key=lambda item: item[1], reverse=True)
        ranking = []
        for index, (user_id, xp) in enumerate(sorted_users[:10], start=1):  # Mostrar solo los primeros 10
            user = ctx.guild.get_member(user_id)
            username = user.name if user else f"Usuario desconocido ({user_id})"
            
            # Asignar emojis según la posición
            if index == 1:
                emoji = "🥇"
            elif index == 2:
                emoji = "🥈"
            elif index == 3:
                emoji = "🥉"
            else:
                emoji = "🏅"
            
            ranking.append(f"{emoji} **#{index}** {username} - **{xp} XP**")

        # Verificar si el usuario que ejecuta el comando está fuera del top 10
        user_xp_position = next((i + 1 for i, (user_id, _) in enumerate(sorted_users) if user_id == ctx.author.id), None)
        if user_xp_position and user_xp_position > 10:
            user_xp_value = user_xp[ctx.author.id]
            ranking.append(
                f"\n🔽 **Tu posición:** #{user_xp_position} - **{user_xp_value} XP**\n"
                f"¡Sigue participando para entrar en el top 10!"
            )

        embed = discord.Embed(
            title="🏆 Ranking de Usuarios",
            description="\n".join(ranking) if ranking else "No hay usuarios en el ranking.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/previews/011/048/332/original/sports-championship-gold-trophy-icon-png.png")  # Icono decorativo
        embed.set_footer(text="¡Sigue participando para mejorar tu posición!")
        await ctx.send(embed=embed)

    @bot.command(name="progreso")
    @commands.cooldown(1, 1800, commands.BucketType.user)  # 1 uso cada 1800 segundos (30 minutos) por usuario
    async def check_progress(ctx, member: discord.Member = None):
        member = member or ctx.author
        xp = user_xp.get(member.id, 0)
        next_rank = None

        # Buscar el siguiente rango
        for rank in RANKS:
            if xp < rank["xp_required"]:
                next_rank = rank
                break

        if next_rank:
            xp_needed = next_rank["xp_required"] - xp
            total_xp_for_rank = next_rank["xp_required"]
            progress_percentage = (xp / total_xp_for_rank) * 100 if total_xp_for_rank > 0 else 0

            # Crear barra de progreso
            progress_bar_length = 30
            filled_length = int(progress_bar_length * (xp / total_xp_for_rank)) if total_xp_for_rank > 0 else 0
            progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)

            embed = discord.Embed(
                title="📈 Progreso hacia el siguiente rango",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.add_field(
                name="Rango Actual",
                value=f"🏅 **{RANKS[max(0, len([r for r in RANKS if xp >= r['xp_required']]) - 1)]['name']}**",
                inline=True
            )
            embed.add_field(
                name="Siguiente Rango",
                value=f"🎯 **{next_rank['name']}**",
                inline=True
            )
            embed.add_field(
                name="XP Necesario",
                value=f"📊 **{xp_needed} XP** restantes",
                inline=False
            )
            embed.add_field(
                name="Progreso",
                value=f"`[{progress_bar}] {progress_percentage:.2f}%`",
                inline=False
            )
            embed.set_footer(
                text=f"¡Sigue participando para alcanzar el rango {next_rank['name']}!",
                icon_url="https://cdn-icons-png.flaticon.com/512/847/847969.png"
            )
        else:
            embed = discord.Embed(
                title="🎉 ¡Has alcanzado el rango más alto!",
                description=f"{member.mention} ya tiene el rango **{RANKS[-1]['name']}**.",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.set_footer(
                text="¡Felicidades por alcanzar el rango más alto!",
                icon_url="https://cdn-icons-png.flaticon.com/512/847/847969.png"
            )

        await ctx.send(embed=embed)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            print(f"DEBUG: Cooldown activo para el comando '{ctx.command.name}'. Tiempo restante: {error.retry_after:.2f} segundos.")
            # Personalizar el mensaje de cooldown para `!progreso` y `!rank`
            if ctx.command.name in ["progreso", "rank"]:
                retry_after = int(error.retry_after)
                minutes, seconds = divmod(retry_after, 60)
                hours, minutes = divmod(minutes, 60)

                embed = discord.Embed(
                    title="⏳ Cooldown Activo",
                    description=(
                        f"El comando **!{ctx.command.name}** está en cooldown.\n\n"
                        f"**Tiempo restante:** {hours}h {minutes}m {seconds}s"
                    ),
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Gracias por tu paciencia.")
                await ctx.send(embed=embed, delete_after=10)
            else:
                # Mensaje genérico para otros comandos (opcional)
                retry_after = int(error.retry_after)
                minutes, seconds = divmod(retry_after, 60)
                hours, minutes = divmod(minutes, 60)

                embed = discord.Embed(
                    title="⏳ Comando en Cooldown",
                    description=(
                        f"Por favor, espera antes de usar este comando nuevamente.\n\n"
                        f"**Tiempo restante:** {hours}h {minutes}m {seconds}s"
                    ),
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Gracias por tu paciencia.")
                await ctx.send(embed=embed, delete_after=10)
        else:
            print(f"DEBUG: Error no manejado: {error}")
            # Manejar otros errores (opcional)
            raise error