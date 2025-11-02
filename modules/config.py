import os
import json
from modules.colorFunctions import Color

DEFAULT_CONFIG = {
    "MAIN_COLOR": "#ffffff",
    "ERROR_COLOR": "#f44336",
    "FONT_PATH": "font.ttf",
    "DB_PATH": "db_v5.sqlite",
    "OWNER": 747936027049721946,
    "TOKEN": ""
}

class Config:
    """Конфигурация бота."""
    def __init__(self, config_path: str) -> None:
        self._path = config_path
        self._ensure_exists()
        self._load()

    def _ensure_exists(self) -> None:
        """Создать config.json, если он отсутствует."""
        if not os.path.exists(self._path):
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
            print(f"[Config] Файл {self._path} не найден, создан новый шаблон.")

    def get_token(self) -> str:
        return self.__token
    
    def _load(self) -> None:
        """Загрузить конфигурацию из файла."""
        with open(self._path, encoding='utf-8') as f:
            self._data = json.load(f)
        self._emojis: dict = self._data.get("EMOJIS", {})
        self.MAIN_COLOR = Color(self._data.get("MAIN_COLOR", "#FFFFFF")).disnakeColor
        self.ERROR_COLOR = Color(self._data.get("ERROR_COLOR", "#FF0000")).disnakeColor
        self.FONT_PATH = self._data.get("FONT_PATH")
        self.DB_PATH = self._data.get("DB_PATH", "db.sqlite")
        self.OWNER = self._data.get("OWNER", None)
        self.__token = self._data.get("TOKEN")

cfg = Config('config.json')
