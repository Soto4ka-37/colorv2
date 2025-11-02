import disnake
from disnake.ext import commands
from modules.config import cfg
from modules.database import db
from disnake.ext import commands
import disnake
import asyncio

intents = disnake.Intents.none()
intents.guild_messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=cfg.OWNER, help_command=None)

async def prepare():
    """Подготовка перед запуском бота"""
    # Инициализация базы данных
    await db.init()
    # Загрузка модулей
    bot.i18n.load('locale')
    bot.load_extensions('cogs')
    bot.load_extension('jishaku')
    
async def shutdown():
    """Корректное завершение"""
    print('Завершение работы')
    # Закрываем соединение с БД
    await db.close()

async def main():
    await prepare()

if __name__ == "__main__":
    try:
        # Сначала подготовка
        asyncio.run(main())
        # Подключение к дискорду
        bot.run(cfg.get_token())
        
    finally:
        # Правильно завершаем работу
        asyncio.run(shutdown())
