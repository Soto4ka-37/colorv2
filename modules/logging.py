import aiohttp
import requests
from enum import Enum
from typing import Dict

from modules.config import cfg

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {cfg.LOG_TOKEN}"
}

class LogType(Enum):
    CRASH = 1
    EXCEPTION = 2
    MESSAGE = 3

LOG_CONFIGS: Dict[LogType, str] = {
    LogType.CRASH: 'crash',
    LogType.EXCEPTION: 'exception',
    LogType.MESSAGE: 'message'
}

def log(log_type: LogType, event_type: str, details: str, trigger: str):
    url = f'{cfg.LOG_HOST}/api/log'
    json = {
        "log_type": LOG_CONFIGS.get(log_type),
        "event_type": str(event_type),
        "details": str(details),
        "trigger": str(trigger)
    }
    
    response = requests.post(url, headers=headers, json=json)
    if response.status_code == 200:
        return response.json()
    
async def logAsync(log_type: LogType, event_type: str, details: str, trigger: str):
    url = f'{cfg.LOG_HOST}/api/log'

    json = {
        "log_type": LOG_CONFIGS.get(log_type),
        "event_type": str(event_type),
        "details": str(details),
        "trigger": str(trigger)
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json) as response:
            if response.status == 200:
                await response.json()
