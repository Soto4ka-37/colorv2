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
                "DB": "",
                "CHIP": "",
                "STATS": "",
                "CLOCK": "",
                "STORAGE": "",
                "LEFT_ARROW": "",
                "RIGHT_ARROW": "",
                "CROSS": "",
                "CHECKMARK": "",
                "LAYERS": "",
                "INFO": "",
                "WARNING": "",
                "ERROR": "",
                "FORBIDDEN": "",
                "SPEEDOMETER": "",
                "ONLINE": "",
                "OFFLINE": "",
                "GEAR": "",
                "KEY": "",
                "HELP": ""
            }
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)

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
        self.FORBIDDEN: str = self._data.get('FORBIDDEN', '')
        self.GEAR: str = self._data.get('GEAR', '')
        self.KEY: str = self._data.get('KEY', '')
        self.HELP: str = self._data.get('HELP', '')

emoji = Emojis('emojis.json')