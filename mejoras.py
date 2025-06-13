import discord

BOOST_ROLE_ID = 1383011769768738816
BOOST_CHANNEL_ID = 1381937912446451732

def setup_mejoras(bot):
    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        # Detectar si el usuario acaba de boostear el servidor
        if not before.premium_since and after.premium_since:
            # Asignar el rol de booster
            role = after.guild.get_role(BOOST_ROLE_ID)
            if role:
                try:
                    await after.add_roles(role, reason="¡Gracias por mejorar el servidor!")
                except Exception as e:
                    print(f"Error al asignar el rol de booster: {e}")

            # Enviar mensaje profesional e impactante al canal de boosts
            channel = after.guild.get_channel(BOOST_CHANNEL_ID)
            if channel:
                try:
                    embed = discord.Embed(
                        title="🚀 ¡Nuevo impulso al servidor! 🚀",
                        description=(
                            f"✨ {after.mention} ha mejorado **Deadly Clan** con un boost.\n\n"
                            "¡Gracias por tu apoyo y confianza! 💜\n"
                            "Tu contribución nos ayuda a crecer y a ofrecer una mejor experiencia para todos.\n\n"
                            "¡Eres parte fundamental de nuestra comunidad! 🎉"
                        ),
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=after.avatar.url if after.avatar else discord.Embed.Empty)
                    embed.set_footer(text="Deadly Clan • ¡Gracias por impulsar el servidor!")
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error al enviar mensaje de boost: {e}")
