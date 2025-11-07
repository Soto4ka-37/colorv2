import os
import json
# Конфиг core_connect.json
class Emojis:
    """Главная конфигурация проекта"""
    def __init__(self, config_path: str) -> None:
        self._path = config_path
        self._ensure_exists()
        self._load()
        
    def _ensure_exists(self) -> None:
        if not os.path.exists(self._path):
            default_data = {
                "LOADING": "",
                "LEFT_ARROW": "",
                "RIGHT_ARROW": "",
                "CROSS": "",
                "CHECKMARK": "",
                "INFO": "",
                "ERROR": "",
                "WARNING": "",
                "FORBIDDEN": "",
                "GEAR": "",
                "KEY": "",
                "HELP": "",
                "CLOCK": "",
                "LOUPE": "",
                "DICE": "",
                "PAINT": "",
                "HAMMER": "",
                "SHIELD": "",
                "CHAT": ""
            }
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            print(f"[Config] Файл {self._path} не найден, создан новый шаблон.")

    def _load(self) -> None:
        with open(self._path, encoding='utf-8') as f:
            self._data: dict = json.load(f)

        self.LOADING: str = self._data.get('LOADING', '')
        self.LEFT_ARROW: str = self._data.get('LEFT_ARROW', '')
        self.RIGHT_ARROW: str = self._data.get('RIGHT_ARROW', '')
        self.CROSS: str = self._data.get('CROSS', '')
        self.CHECKMARK: str = self._data.get('CHECKMARK', '')
        self.INFO: str = self._data.get('INFO', '')
        self.ERROR: str = self._data.get('ERROR', '')
        self.WARNING: str = self._data.get('WARNING', '')
        self.FORBIDDEN: str = self._data.get('FORBIDDEN', '')
        self.GEAR: str = self._data.get('GEAR', '')
        self.KEY: str = self._data.get('KEY', '')
        self.HELP: str = self._data.get('HELP', '')
        self.CLOCK: str = self._data.get('CLOCK', '')
        self.LOUPE: str = self._data.get('LOUPE', '')
        self.DICE: str = self._data.get('DICE', '')
        self.PAINT: str = self._data.get('PAINT', '')
        self.HAMMER: str = self._data.get('HAMMER', '')
        self.SHIELD: str = self._data.get('SHIELD', '')
        self.CHAT: str = self._data.get('CHAT', '')

emoji = Emojis('emojis.json')