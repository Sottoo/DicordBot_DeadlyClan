import discord
from discord.ext import commands
from collections import defaultdict
import asyncio
import time

# Diccionario para rastrear mensajes por usuario
user_message_count = defaultdict(list)

# Diccionario para rastrear advertencias y timestamps de castigos
user_warnings = defaultdict(list)  # {user_id: [timestamp1, timestamp2, ...]}

# Diccionario para evitar múltiples castigos en ráfaga
user_last_punish = defaultdict(float)  # {user_id: timestamp}

# Configuración de detección de spam
SPAM_THRESHOLD = 5  # Número de mensajes permitidos en el intervalo
SPAM_INTERVAL = 10  # Intervalo de tiempo en segundos

# Castigos progresivos en segundos: 1min, 5min, 1h, 1d, ban
PUNISHMENTS = [60, 300, 3600, 86400, "ban"]

# Tiempo mínimo entre castigos para el mismo usuario (antiflood de castigos)
MIN_TIME_BETWEEN_PUNISH = 60  # segundos (ajusta este valor para más tolerancia)

# Diccionario para rastrear tareas de silencio activas
active_mute_tasks = {}  # {user_id: asyncio.Task}

async def detect_spam(message: discord.Message):
    if message.author.bot:
        return  # Ignorar mensajes de bots

    user_id = message.author.id
    current_time = message.created_at.timestamp()

    # Registrar el mensaje
    user_message_count[user_id].append(current_time)

    # Eliminar mensajes fuera del intervalo
    user_message_count[user_id] = [
        timestamp for timestamp in user_message_count[user_id]
        if current_time - timestamp <= SPAM_INTERVAL
    ]

    # Detectar spam solo si no ha sido castigado recientemente
    if len(user_message_count[user_id]) > SPAM_THRESHOLD:
        last_punish = user_last_punish.get(user_id, 0)
        if current_time - last_punish > MIN_TIME_BETWEEN_PUNISH:
            await handle_spam(message)
            user_last_punish[user_id] = current_time
        try:
            await message.delete()
        except Exception:
            pass  # Ignorar si no puede borrar el mensaje

async def handle_spam(message: discord.Message):
    guild = message.guild
    member = message.author
    user_id = member.id
    now = time.time()

    # Limpiar advertencias viejas (solo cuenta reincidencias en los últimos 2 días)
    user_warnings[user_id] = [t for t in user_warnings[user_id] if now - t < 2 * 86400]

    # Determinar nivel de castigo
    warning_count = len(user_warnings[user_id])
    if warning_count >= len(PUNISHMENTS):
        warning_count = len(PUNISHMENTS) - 1

    punishment = PUNISHMENTS[warning_count]
    user_warnings[user_id].append(now)

    mute_role_name = "Muteado"
    mute_role = discord.utils.get(guild.roles, name=mute_role_name)

    # Crear el rol si no existe
    if mute_role is None and punishment != "ban":
        try:
            mute_role = await guild.create_role(
                name=mute_role_name,
                reason="Rol para silenciar usuarios por spam"
            )
            for channel in guild.text_channels:
                await channel.set_permissions(mute_role, send_messages=False)
        except discord.Forbidden:
            embed = discord.Embed(
                title="Permiso insuficiente",
                description="🚫 No tengo permisos para crear el rol de muteo.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, delete_after=10)
            return
        except Exception as e:
            print(f"⚠️ Error al crear el rol de muteo: {e}")
            return

    try:
        if punishment == "ban":
            await member.ban(reason="Ban automático por reincidencia de spam")
            embed = discord.Embed(
                title="Usuario baneado por spam",
                description=f"{member.mention} ha sido baneado permanentemente por no entender.",
                color=discord.Color.dark_red()
            )
            await message.channel.send(embed=embed, delete_after=20)
            return

        # Cancelar cualquier tarea de silencio activa para evitar conflictos
        if user_id in active_mute_tasks:
            active_mute_tasks[user_id].cancel()
            del active_mute_tasks[user_id]

        await member.add_roles(mute_role, reason="Silenciado por spam")

        # Mensaje embed en el canal
        embed = discord.Embed(
            title="Usuario sancionado por spam",
            description=f"{member.mention} ha sido silenciado temporalmente.",
            color=discord.Color.orange()
        )
        if warning_count == 0:
            embed.add_field(name="Duración", value="1 minuto", inline=True)
        elif warning_count == 1:
            embed.add_field(name="Duración", value="5 minutos", inline=True)
        elif warning_count == 2:
            embed.add_field(name="Duración", value="1 hora", inline=True)
        elif warning_count == 3:
            embed.add_field(name="Duración", value="1 día", inline=True)
        embed.add_field(name="Motivo", value="Detección automática de spam", inline=True)
        embed.set_footer(text=f"Advertencia #{warning_count+1} • El equipo de moderación ha sido notificado.")
        await message.channel.send(embed=embed, delete_after=15)

        # Crear y almacenar la tarea de silencio
        mute_task = asyncio.create_task(asyncio.sleep(punishment))
        active_mute_tasks[user_id] = mute_task
        await mute_task

        # Remover el rol después del tiempo de silencio
        await member.remove_roles(mute_role, reason="Fin del silencio por spam")
        del active_mute_tasks[user_id]

        # Mensaje embed al canal al finalizar el muteo
        embed_unmute = discord.Embed(
            title="Silencio levantado",
            description=f"{member.mention} ya puede enviar mensajes nuevamente.",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed_unmute, delete_after=10)
    except asyncio.CancelledError:
        # Si la tarea es cancelada, limpiar el rol y salir
        if mute_role in member.roles:
            await member.remove_roles(mute_role, reason="Silencio cancelado manualmente")
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permiso insuficiente",
            description="🚫 No tengo permisos para modificar los roles o banear a este usuario.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed, delete_after=10)
    except Exception as e:
        print(f"⚠️ Error al manejar el spam: {e}")

def setup_spam_commands(bot):
    @bot.command(name="unsilence")
    @commands.has_permissions(administrator=True)
    async def unsilence(ctx, member: discord.Member):
        mute_role_name = "Muteado"
        mute_role = discord.utils.get(ctx.guild.roles, name=mute_role_name)
        user_id = member.id
        if mute_role in member.roles:
            try:
                await member.remove_roles(mute_role, reason="Silencio removido manualmente por un administrador")

                # Cancelar cualquier tarea de silencio activa
                if user_id in active_mute_tasks:
                    active_mute_tasks[user_id].cancel()
                    del active_mute_tasks[user_id]

                # Limpiar advertencias, mensajes y antiflood del usuario
                user_warnings.pop(user_id, None)
                user_message_count.pop(user_id, None)
                user_last_punish.pop(user_id, None)
                embed = discord.Embed(
                    description=f"🔈 El silencio de {member.mention} ha sido removido por algun administrador.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed, delete_after=8)
            except Exception as e:
                await ctx.send("❌ No se pudo remover el silencio. Verifica los permisos del bot.", delete_after=8)
        else:
            # Cancelar cualquier tarea de silencio activa
            if user_id in active_mute_tasks:
                active_mute_tasks[user_id].cancel()
                del active_mute_tasks[user_id]

            # Limpiar registros aunque no tenga el rol, por si acaso
            user_warnings.pop(user_id, None)
            user_message_count.pop(user_id, None)
            user_last_punish.pop(user_id, None)
            embed = discord.Embed(
                description=f"{member.mention} no está silenciado. Registros limpiados.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed, delete_after=8)

    @bot.command(name="unban")
    @commands.has_permissions(administrator=True)  # Restringir a administradores
    async def unban(ctx, user: discord.User):
        try:
            await ctx.guild.unban(user, reason="Ban removido manualmente por un administrador")
            embed = discord.Embed(
                description=f"✅ El ban de {user.mention} ha sido removido.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=8)
        except Exception as e:
            await ctx.send(f"❌ No se pudo remover el ban de {user.mention}.", delete_after=8)

    @bot.command(name="ban")
    @commands.has_permissions(administrator=True)
    async def ban(ctx, member: discord.Member, *, reason="No especificado"):
        try:
            await member.ban(reason=f"Ban manual por administrador: {reason}")
            embed = discord.Embed(
                description=f"🚫 {member.mention} ha sido baneado.\n**Razón:** {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        except Exception as e:
            await ctx.send(f"❌ No se pudo banear a {member.mention}. Verifica los permisos del bot.", delete_after=8)
