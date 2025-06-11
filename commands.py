import discord  
from discord.ext import commands

@commands.has_permissions(administrator=True)  # Solo administradores pueden usar este comando
async def reglas(ctx):
    embed = discord.Embed(
        title="📜 REGLAS DEL SERVIDOR",
        description=(
            "**Por favor, lee y sigue estas reglas para mantener un ambiente agradable para todos.**\n\n"
            "**1️⃣ Respeto:** Respeta a todos los miembros del servidor. No se tolerará ningún tipo de acoso, insultos o comportamiento tóxico.\n"
            "**2️⃣ No Spam:** Evita hacer spam, flood o enviar mensajes repetitivos.\n"
            "**3️⃣ Contenido Apropiado:** Está prohibido compartir contenido NSFW o cualquier material ofensivo.\n"
            "**4️⃣ Uso Correcto de Canales:** Asegúrate de usar los canales para los propósitos indicados.\n"
            "**5️⃣ Promoción:** No promociones otros servidores o enlaces externos sin el permiso de un administrador.\n\n"
            "✅ **Reacciona con ✅ para aceptar las reglas y obtener acceso al servidor.**\n\n"
            "¡Gracias por ser parte de nuestra comunidad! 🎉"
        ),
        color=discord.Color.red()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/976730518420860930/1381160264665141378/540a13f9-dca9-40d2-8c9a-cfef7c093e60.png?ex=6846813b&is=68452fbb&hm=d0cba415c9e55fc72c0f1b333d7449021c9ae52c41a358387ec7e7744b6743f9&")  
    msg = await ctx.send(embed=embed)
    try:
        await msg.add_reaction("✅")
    except Exception as e:
        await ctx.send("No se pudo agregar la reacción. Verifica los permisos del bot.")

def setup_commands(bot):
    bot.command(name='reglas')(reglas)

    @bot.event
    async def on_raw_reaction_add(payload):
        guild = discord.utils.get(bot.guilds, id=payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.emoji.name == "✅" and member:
            role = discord.utils.get(guild.roles, name="Miembro")  # Cambia "Miembro" por el nombre del rol deseado
            if role and role not in member.roles:
                await member.add_roles(role, reason="Aceptó las reglas del servidor")

    @bot.event
    async def on_raw_reaction_remove(payload):
        guild = discord.utils.get(bot.guilds, id=payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.emoji.name == "✅" and member:
            role = discord.utils.get(guild.roles, name="Miembro")  # Cambia "Miembro" por el nombre del rol deseado
            if role and role not in member.roles:
                await member.add_roles(role, reason="Aceptó las reglas del servidor nuevamente")