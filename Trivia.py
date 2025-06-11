import discord
import random
import asyncio
from discord.ext import commands

@commands.command(name="trivia")
async def trivia(ctx):
    preguntas = []
    with open("d:\\BOT CORD_Deadly\\Trivia_Preguntas.txt", "r", encoding="utf-8") as archivo:
        for linea in archivo:
            partes = linea.strip().split("|")
            preguntas.append({
                "pregunta": partes[0],
                "opciones": partes[1].split(","),
                "respuesta": partes[2]
            })

    trivia = random.choice(preguntas)
    opciones = "\n".join(trivia["opciones"])
    embed = discord.Embed(
        title="🎮 Trivia de Valorant",
        description=f"{trivia['pregunta']}\n\n{opciones}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Responde con A, B, C o D.")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.content.upper() in ["A", "B", "C", "D"]

    try:
        respuesta = await ctx.bot.wait_for("message", timeout=30.0, check=check)
        if respuesta.content.upper() == trivia["respuesta"]:
            embed_correcto = discord.Embed(
                title="✅ ¡Respuesta Correcta! 🎉",
                description="¡Bien hecho! Has acertado la respuesta.",
                color=discord.Color.green()
            )
            embed_correcto.add_field(name="Pregunta", value=trivia["pregunta"], inline=False)
            embed_correcto.add_field(name="Tu respuesta", value=respuesta.content.upper(), inline=True)
            await ctx.send(embed=embed_correcto)
        else:
            embed_incorrecto = discord.Embed(
                title="❌ Respuesta Incorrecta 😔",
                description=f"La respuesta correcta era **{trivia['respuesta']}**.",
                color=discord.Color.red()
            )
            embed_incorrecto.add_field(name="Pregunta", value=trivia["pregunta"], inline=False)
            embed_incorrecto.add_field(name="Tu respuesta", value=respuesta.content.upper(), inline=True)
            embed_incorrecto.set_footer(text="¡Sigue intentando, puedes mejorar!")
            await ctx.send(embed=embed_incorrecto)
    except asyncio.TimeoutError:
        await ctx.send("⏳ Se acabó el tiempo. ¡Intenta nuevamente!")
