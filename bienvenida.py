from PIL import Image, ImageDraw, ImageFont, ImageFilter
import discord
import os
from io import BytesIO

async def send_welcome_message(member):
    channel = member.guild.get_channel(1381227477614985247)
    if channel is not None:
        try:
            # Verificar si la imagen de fondo existe
            bg_path = "welcome_background.jpg"
            if not os.path.isfile(bg_path):
                print(f"⚠️ Imagen de fondo '{bg_path}' no encontrada.")
                return

            # Cargar la imagen de fondo y verificar resolución mínima
            background = Image.open(bg_path).convert("RGBA")
            min_width, min_height = 700, 350
            width, height = background.size
            if width < min_width or height < min_height:
                print(f"⚠️ La imagen de fondo es muy pequeña. Se recomienda al menos {min_width}x{min_height}px.")
                background = background.resize((min_width, min_height))
                width, height = min_width, min_height

            # Difumina mucho más el fondo (casi no se nota la imagen)
            blurred_bg = background.filter(ImageFilter.GaussianBlur(radius=25))

            # Tamaños y márgenes consistentes
            avatar_diameter = 170
            border_size = 8
            shadow_size = 16
            total_size = avatar_diameter + border_size*2 + shadow_size*2
            top_margin = 30
            spacing = 18

            # Descargar el avatar del usuario usando discord.py (sin requests)
            try:
                avatar_asset = member.avatar or member.default_avatar
                avatar_bytes = await avatar_asset.read()
                avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
            except Exception as e:
                print(f"⚠️ Error al descargar el avatar: {e}")
                avatar = Image.new("RGBA", (avatar_diameter, avatar_diameter), (100,100,100,255))

            # Redimensionar avatar manteniendo proporción y recortar si es necesario
            avatar = avatar.resize((avatar_diameter, avatar_diameter), Image.LANCZOS)

            # Crear máscara circular para el avatar
            mask = Image.new("L", (avatar_diameter, avatar_diameter), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_diameter, avatar_diameter), fill=255)

            # Crear borde y sombra para el avatar
            avatar_layer = Image.new("RGBA", (total_size, total_size), (0,0,0,0))

            # Sombra
            shadow = Image.new("RGBA", (avatar_diameter + shadow_size*2, avatar_diameter + shadow_size*2), (0,0,0,0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.ellipse((0, 0, avatar_diameter + shadow_size*2, avatar_diameter + shadow_size*2), fill=(0,0,0,120))
            avatar_layer.paste(shadow, (0,0), shadow)

            # Borde blanco
            border = Image.new("RGBA", (avatar_diameter + border_size*2, avatar_diameter + border_size*2), (0,0,0,0))
            border_draw = ImageDraw.Draw(border)
            border_draw.ellipse((0, 0, avatar_diameter + border_size*2, avatar_diameter + border_size*2), fill=(255,255,255,255))
            avatar_layer.paste(border, (shadow_size, shadow_size), border)

            # Avatar circular
            avatar_layer.paste(avatar, (border_size + shadow_size, border_size + shadow_size), mask)

            # Redimensionar la imagen de fondo a un tamaño más alto para más espacio vertical
            target_width, target_height = 700, 450  # Antes: 700x350
            if (width, height) != (target_width, target_height):
                blurred_bg = blurred_bg.resize((target_width, target_height), Image.LANCZOS)
                width, height = target_width, target_height

            # Posicionar avatar centrado arriba
            avatar_x = (width - total_size) // 2
            avatar_y = top_margin
            blurred_bg.paste(avatar_layer, (avatar_x, avatar_y), avatar_layer)

            # Preparar fuente
            try:
                font = ImageFont.truetype("Jersey15-Regular.ttf", 40)
                font_small = ImageFont.truetype("Jersey15-Regular.ttf", 28)
            except OSError:
                print("⚠️ Fuente 'arial.ttf' no encontrada. Usa una fuente válida.")
                return

            # Texto de bienvenida (más atractivo)
            welcome_text = "✨ ¡Bienvenido/a a Deadly Clan! ✨"
            user_text = f"{member.name}#{member.discriminator}"
            server_text = f"Te damos la bienvenida a {member.guild.name}"

            draw = ImageDraw.Draw(blurred_bg)

            # Función para dibujar texto con sombra y borde, centrado exacto
            def draw_text_with_effect_centered(draw, y, text, font, fill, shadow_color=(0,0,0,180), border_color=(255,255,255,180), offset=3, border=2):
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                # Sombra
                draw.text((x+offset, y+offset), text, font=font, fill=shadow_color)
                # Borde
                for dx in range(-border, border+1):
                    for dy in range(-border, border+1):
                        if dx != 0 or dy != 0:
                            draw.text((x+dx, y+dy), text, font=font, fill=border_color)
                # Texto principal
                draw.text((x, y), text, font=font, fill=fill)

            # Centrar textos usando getbbox
            def get_text_height(font, text):
                bbox = font.getbbox(text)
                return bbox[3] - bbox[1]

            h_welcome = get_text_height(font, welcome_text)
            h_user = get_text_height(font, user_text)
            h_server = get_text_height(font_small, server_text)

            # Calcular altura total de los textos y espacios
            total_text_height = h_welcome + 18 + h_user + 14 + h_server
            # Centrar el bloque de texto verticalmente debajo del avatar
            text_block_start = avatar_y + total_size + ((height - (avatar_y + total_size)) - total_text_height) // 2

            welcome_y = text_block_start
            user_y = welcome_y + h_welcome + 18
            server_y = user_y + h_user + 14

            # Colores personalizados
            red_soft = (220, 50, 50)  # Rojo no saturado
            silver = (200, 200, 210)  # Plateado suave

            # Dibujar textos con efecto atractivo y centrado
            draw_text_with_effect_centered(draw, welcome_y, welcome_text, font, fill=red_soft, shadow_color=(0,0,0,200), border_color=(255,255,255,180), offset=4, border=2)
            draw_text_with_effect_centered(draw, user_y, user_text, font, fill=silver, shadow_color=(0,0,0,180), border_color=(255,255,255,120), offset=3, border=1)
            draw_text_with_effect_centered(draw, server_y, server_text, font_small, fill="#ffffff", shadow_color=(0,0,0,180), border_color=(255,255,255,120), offset=2, border=1)

            # Guardar la imagen final
            output_path = f"welcome_{member.id}.png"
            blurred_bg.save(output_path)

            # Enviar solo la imagen al canal
            await channel.send(file=discord.File(output_path))

            # Eliminar el archivo generado
            os.remove(output_path)
        except Exception as e:
            print(f"⚠️ Error al generar la imagen de bienvenida: {e}")
        except Exception as e:
            print(f"⚠️ Error al generar la imagen de bienvenida: {e}")
