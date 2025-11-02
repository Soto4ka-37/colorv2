import json
from modules.colorFunctions import Color

class Config:
    """Конфигурация бота."""
    def __init__(self, config_path: str) -> None:
        self._path = config_path
        self._load()

    def get_token(self) -> str:
        return self.__token
    
    def _load(self) -> None:
        """Загрузить конфигурацию из файла."""
        with open(self._path, encoding='utf-8') as f:
            self._data = json.load(f)
        self._emojis: dict = self._data.get("EMOJIS", {})
        self.MAIN_COLOR = Color(self._data.get("MAIN_COLOR", "FFFFFF")).disnakeColor
        self.ERROR_COLOR = Color(self._data.get("ERROR_COLOR", "FF0000")).disnakeColor
        self.FONT_PATH = self._data.get("FONT_PATH")
        self.DB_PATH = self._data.get("DB_PATH", 'db.sqlite')
        self.OWNER = self._data.get("OWNER", None)
        self.__token = self._data.get("TOKEN")

cfg = Config('config.json')
