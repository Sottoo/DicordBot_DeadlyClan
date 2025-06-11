import discord
import asyncio
import random
from discord.ext import commands
from datetime import datetime, timedelta

# Registrar el último uso del comando por servidor
ultimo_uso_servidor = {}

@commands.command(name="sondeo")
async def sondeo(ctx, encuesta_id: int = None):  # Agregar valor predeterminado
    global ultimo_uso_servidor

    # Verificar si el comando fue usado recientemente en el servidor
    if ctx.guild.id in ultimo_uso_servidor:
        tiempo_restante = (ultimo_uso_servidor[ctx.guild.id] + timedelta(minutes=30)) - datetime.now()
        if tiempo_restante.total_seconds() > 0:
            minutos, segundos = divmod(tiempo_restante.total_seconds(), 60)
            embed = discord.Embed(
                title="⏳ Cooldown Activo",
                description=f"Este comando está en cooldown.\nPor favor, inténtalo nuevamente en **{int(minutos)} minutos y {int(segundos)} segundos**.",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Gracias por tu paciencia.")
            await ctx.send(embed=embed, delete_after=10)
            return

    encuestas = []
    with open("d:\\BOT CORD_Deadly\\sondeo.txt", "r", encoding="utf-8") as archivo:
        for linea in archivo:
            partes = linea.strip().split("|")
            encuestas.append({
                "pregunta": partes[0],
                "opciones": partes[1].split(",")
            })

    # Seleccionar una encuesta aleatoria si no se proporciona ID
    if encuesta_id is None:
        encuesta_id = random.randint(1, len(encuestas))

    if encuesta_id < 1 or encuesta_id > len(encuestas):
        embed = discord.Embed(
            title="❌ ID de Encuesta Inválido",
            description=f"Por favor, elige un número entre 1 y {len(encuestas)}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    # Registrar el momento del uso del comando en el servidor solo si el ID es válido
    ultimo_uso_servidor[ctx.guild.id] = datetime.now()

    encuesta = encuestas[encuesta_id - 1]
    opciones = encuesta["opciones"]
    votos = {opcion.split()[0]: 0 for opcion in opciones}  # Inicializar conteo de votos
    usuarios_votaron = set()  # Registrar usuarios que ya votaron

    def generar_embed():
        total_votos = sum(votos.values())
        opciones_texto = "\n".join([f"{opcion.split()[0]}: {opcion.split()[1]}" for opcion in opciones])
        grafica = ""
        for opcion in opciones:
            opcion_texto = opcion.split()[0]
            porcentaje = (votos[opcion_texto] / total_votos * 100) if total_votos > 0 else 0
            barra_progreso = "█" * int(porcentaje // 10) + "░" * (10 - int(porcentaje // 10))
            grafica += f"{opcion_texto}: {votos[opcion_texto]} votos ({porcentaje:.1f}%)\n{barra_progreso}\n\n"

        embed = discord.Embed(
            title="📊 Encuesta Activa",
            description=f"**{encuesta['pregunta']}**\n\n**Opciones:**\n{opciones_texto}\n\n{grafica}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="¡Vota ahora! Tienes 60 segundos para participar.")
        embed.set_author(name="Sistema de Encuestas", icon_url="https://example.com/icon.png")
        embed.timestamp = datetime.now()
        return embed

    mensaje = await ctx.send(embed=generar_embed())

    for opcion in ["🅰️", "🅱️", "🇨", "🇩"]:
        await mensaje.add_reaction(opcion)

    tiempo_expirado = False  # Bandera para controlar el tiempo de votación

    def check_add(reaction, user):
        return not tiempo_expirado and user != ctx.bot.user and reaction.message.id == mensaje.id and str(reaction.emoji) in votos

    def check_remove(reaction, user):
        return not tiempo_expirado and user != ctx.bot.user and reaction.message.id == mensaje.id and str(reaction.emoji) in votos

    try:
        while not tiempo_expirado:  # Permitir múltiples reacciones hasta que se agote el tiempo
            add_task = asyncio.create_task(ctx.bot.wait_for("reaction_add", check=check_add))
            remove_task = asyncio.create_task(ctx.bot.wait_for("reaction_remove", check=check_remove))
            done, pending = await asyncio.wait(
                [add_task, remove_task],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=60.0
            )

            for task in done:
                reaction, user = await task
                if task == add_task:
                    if user.id not in usuarios_votaron:  # Solo permitir votar si no ha votado antes
                        votos[reaction.emoji] += 1
                        usuarios_votaron.add(user.id)
                    else:
                        await mensaje.remove_reaction(reaction.emoji, user)  # Eliminar reacción duplicada
                elif task == remove_task:
                    votos[reaction.emoji] = max(0, votos[reaction.emoji] - 1)  # Evitar conteo negativo
                    usuarios_votaron.discard(user.id)  # Permitir votar nuevamente si se elimina la reacción
                await mensaje.edit(embed=generar_embed())  # Actualizar el embed en tiempo real
    except asyncio.TimeoutError:
        tiempo_expirado = True
        embed = discord.Embed(
            title="⏳ Sondeo Finalizado",
            description="El sondeo ha terminado. Aquí están los resultados finales:",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=10)
        await mensaje.edit(embed=generar_embed())
