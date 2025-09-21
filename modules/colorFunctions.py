import disnake
import random
import numpy as np

from exceptions import ColorFormateException
from matplotlib import colors
from modules.otherFunctions import runBlocking

XKCD_NAMES = np.array(list(colors.XKCD_COLORS.keys()))
XKCD_HEX = list(colors.XKCD_COLORS.values())

def hexToRgbNp(hex_color: str) -> np.ndarray:
    """Конвертация hex в RGB массив NumPy"""
    hex_color = hex_color.lstrip('#')
    return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=np.int16)

XKCD_RGB = np.array([hexToRgbNp(h) for h in XKCD_HEX], dtype=np.int16)

class Color:
    def __init__(self, hex_color: str | None):
        '''Класс для работы с цветами
        hex_color: строка в формате HEX, например #FFA500 или FFA500
        Свойства:
        - int: цвет в формате 0xRRGGBB
        - hex: цвет в формате #RRGGBB
        - text: цвет в формате RRGGBB (без #)
        - rgb: цвет в формате (R, G, B)
        - disnakeColor: цвет в формате disnake.Color
        '''

        if hex_color is None:
            raise ColorFormateException("Неверный формат цвета! Используйте HEX, например #FFA500 или fafafa.")
        if isinstance(hex_color, Color):
            self.int = hex_color.int
            self.hex = hex_color.hex
            self.text = hex_color.text
            self.rgb = hex_color.rgb
            self.disnakeColor = hex_color.disnakeColor
            return
        s = hex_color.strip().lstrip('#')
        try:
            v = int(s, 16)
        except ValueError:
            raise ColorFormateException("Неверный формат цвета! Используйте HEX, например #FFA500 или fafafa.")
        if v < 0 or v > 0xFFFFFF:
            raise ColorFormateException("Неверный формат цвета! Используйте HEX, например #FFA500 или fafafa.")
        
        self.int = v
        self.hex = f"#{v:06x}".upper()
        self.text = f"{v:06x}".upper()
        self.rgb = Color.hexToRgbTuple(self.hex)
        self.disnakeColor = disnake.Color(self.int)
        
    def _getName(self) -> tuple[str, str]:
        '''Определяет название цвета по его hex-коду с помощью библиотеки matplotlib и xkcd.'''
        rgb = self.hexToRgbNp(self.hex)
        diff = XKCD_RGB - rgb
        dist = np.linalg.norm(diff, axis=1)

        idx = np.argmin(dist)
        min_dist = dist[idx]

        similarity = max(0.0, 100.0 * (1 - min_dist / 441.67295593))
        similarity = round(similarity, 2)
        similarity = f'{int(similarity)}%'
        color_name = XKCD_NAMES[idx].replace("xkcd:", "")
        return color_name, similarity
                
    async def getName(self) -> tuple[str, str]:
        '''Асинхронная обертка для определения названия цвета.'''
        name, similarity = await runBlocking(self._getName)
        return name, similarity
    
    def __str__(self):
        return self.hex
    
    def __repr__(self):
        return f"Color({self.hex})"
    
    def hexToRgbNp(self, hex_color: str) -> np.ndarray:
        """Конвертация hex в RGB массив NumPy"""
        hex_color = hex_color.lstrip('#')
        return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=np.int16)
    
    def hexToRgbTuple(hex_color: str) -> tuple[int, int, int]:
        """Конвертация hex в RGB кортеж"""
        hex_color = hex_color.lstrip('#')
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

def randomColor() -> Color:
    '''Генерирует случайный цвет'''
    return Color(f'#{random.randint(0, 0xFFFFFF):06x}')
