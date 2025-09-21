import os
import asyncio
from concurrent.futures import ProcessPoolExecutor

_process_executor = None

async def runBlocking(func, *args):
    """
    Универсальный запуск блокирующей функции:
    - при 1 ядре -> asyncio.to_thread (ThreadPoolExecutor)
    - при >1 ядре -> ProcessPoolExecutor (реальный параллелизм)
    """
    cpu_count = os.cpu_count() or 1

    # Если только одно ядро — используем поток
    if cpu_count == 1:
        return await asyncio.to_thread(func, *args)

    # Иначе — общий процессный пул
    global _process_executor
    if _process_executor is None:
        _process_executor = ProcessPoolExecutor(max_workers=cpu_count)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_process_executor, func, *args)

def formatSeconds(value: int):
    """Форматирует секунды в строку вида 1д 2ч 3м 4с"""
    parts = []
    intervals = (
        ('д', 86400),  # 60 * 60 * 24
        ('ч', 3600),   # 60 * 60
        ('м', 60),
        ('с', 1),
    )
    for suffix, length in intervals:
        amount = value // length
        if amount > 0:
            parts.append(f"{amount}{suffix}")
            value -= amount * length
    return ' '.join(parts) if parts else '0с'

def formatBytes(size: int):
    """Форматирует байты в человекочитаемый вид"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"
