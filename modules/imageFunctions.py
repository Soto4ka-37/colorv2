from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
import aiohttp
import disnake
from exceptions import DownloadAvatarException
from sklearn.cluster import KMeans
from modules.otherFunctions import runBlocking
from modules.colorFunctions import Color
from modules.config import cfg

try:
    FONT = ImageFont.truetype(cfg.FONT_PATH, 140)
except IOError:
    FONT = ImageFont.load_default(size=100)

def contrastColorWCAG(color: Color) -> str:
    """
    Определяет, какой цвет (#000000 или #FFFFFF) имеет лучший контраст с данным фоном
    по стандарту WCAG 2.0 (contrast ratio).
    """
    r, g, b = color.rgb

    def to_linear(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    R, G, B = to_linear(r), to_linear(g), to_linear(b)

    L_bg = 0.2126 * R + 0.7152 * G + 0.0722 * B

    contrast_black = (L_bg + 0.05) / 0.05
    contrast_white = (1.05) / (L_bg + 0.05)

    return '#000000' if contrast_black > contrast_white else '#FFFFFF'

def _generateColorImage(color: Color) -> BytesIO:
    """Создает изображение с прямоугольником заданного цвета и текстом по центру."""
    width, height = 500, 250
    
    image = Image.new('RGB', (width, height), color.hex)
    draw = ImageDraw.Draw(image)
    text_color = contrastColorWCAG(color)
    
    text_width, text_height = draw.textbbox((0, 0), color.hex, font=FONT)[2:]  # Используем textbbox
    
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2.5
    
    draw.text((text_x, text_y), color.hex, fill=text_color, font=FONT)
    
    img_io = BytesIO()
    image.save(img_io, format='WEBP')
    img_io.seek(0)
    return img_io

async def generateColorImage(color: Color) -> BytesIO:
    """Асинхронная обертка для генерации цветного изображения."""
    return await runBlocking(_generateColorImage, color)

def _generateFiveColorsImage(colors: list[Color]) -> BytesIO:
    """Создает изображение с несколькими квадратами заданных цветов и номерами по центру."""
    square_size = 250
    count = len(colors)
    width, height = square_size * count, square_size
    image = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(image)

    for i in range(count):
        color = colors[i]

        x0 = i * square_size
        y0 = 0
        x1 = x0 + square_size
        y1 = y0 + square_size
        draw.rectangle([x0, y0, x1, y1], fill=color.hex)

        text = str(i + 1)
        text_color = contrastColorWCAG(color)
        text_bbox = draw.textbbox((0, 0), text, font=FONT)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        text_x = x0 + (square_size - text_width) / 2
        text_y = (square_size - text_height) / 2.5
        draw.text((text_x, text_y), text, fill=text_color, font=FONT)

    img_io = BytesIO()
    image.save(img_io, format='WEBP')
    img_io.seek(0)
    return img_io

async def generateFiveColorsImage(colors: list[Color]) -> BytesIO:
    """Асинхронная обертка для генерации изображения с четырьмя цветами."""
    return await runBlocking(_generateFiveColorsImage, colors)

async def fetchAvatar(user: disnake.User) -> Image.Image:
    if user.avatar:
        url = user.display_avatar.with_format('webp').url
    else:
        url = user.default_avatar.with_format('webp').url

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    img = Image.open(BytesIO(data)).convert('RGBA')
                    return img
                else:
                    raise DownloadAvatarException(
                        'Не удалось скачать аватар пользователя.'
                    )
    except:
        raise DownloadAvatarException(
            'Не удалось скачать аватар пользователя.'
        )

def _getDominantColors(image: Image.Image, count=5, sample_size=50_000):
    """Извлекает доминирующие цвета с помощью KMeans, используя подвыборку пикселей."""
    if image.mode != 'RGB':
        image = image.convert('RGB')

    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)

    # Используем ограниченную выборку для повышения производительности
    if len(pixels) > sample_size:
        idx = np.random.choice(len(pixels), size=sample_size, replace=False)
        pixels = pixels[idx]

    kmeans = KMeans(n_clusters=count, n_init='auto', random_state=42)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_.astype(int)

async def getDominantColors(user: disnake.User, count=5) -> list[Color]:
    """Асинхронная обертка для получения доминирующих цветов аватара пользователя."""
    image = await fetchAvatar(user)
    colors = await runBlocking(_getDominantColors, image, count)
    return [Color(f'#{r:02x}{g:02x}{b:02x}') for r, g, b in colors]
