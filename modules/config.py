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
        # Логгер
        self.LOG_HOST = self._data.get("LOG_HOST")
        self.LOG_TOKEN = self._data.get("LOG_TOKEN")
        # Смайлы
        self.HELP_EMOJI: str = self._emojis.get("HELP", "🆘")
        self.WARNING_EMOJI: str = self._emojis.get("WARNING", "⬆️")
        self.EDIT_ROLE_EMOJI: str = self._emojis.get("EDIT_ROLE", "✏️")
        self.EYE_EMOJI: str = self._emojis.get("EYE", "👀")
        self.PEN_EMOJI: str = self._emojis.get("PEN", "✏️")
        self.IMAGE_EMOJI: str = self._emojis.get("IMAGE", '🖼️')
        self.GEAR_EMOJI: str = self._emojis.get("GEAR", "⚙️")
        self.QUESTION_EMOJI: str = self._emojis.get("QUESTION", '❔')
        self.CROSS_EMOJI: str = self._emojis.get("CROSS", "❌")
        self.CHECKMARK_EMOJI: str = self._emojis.get("CHECKMARK", '✅')
        self.LOADING_EMOJI: str = self._emojis.get("LOADING", '⌛')
        self.TIMER_EMOJI: str = self._emojis.get("TIMER", "⏲️")
        self.BARRIER_EMOJI: str = self._emojis.get("BARRIER", "🚧")
        self.LEFT_ARROW_EMOJI: str = self._emojis.get("LEFT_ARROW", "⬅️")
        self.RIGHT_ARROW_EMOJI: str = self._emojis.get("RIGHT_ARROW", "➡️")


cfg = Config('config.json')
