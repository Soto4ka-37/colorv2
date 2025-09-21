import disnake
import traceback
from disnake.ext import commands

from modules.config import cfg
from modules.database import initDatabase
from modules.logging import LogType, log, logAsync

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), owner_id=cfg.OWNER, help_command=None)

@bot.event
async def on_ready():
    print(f'Авторизован как {bot.user}')
    await logAsync(log_type=LogType.MESSAGE, event_type='ready', details='Соединение установлено', trigger=bot.user)
    
@bot.event
async def on_error(event, *args, **kwargs):
    try:
        await logAsync(log_type=LogType.EXCEPTION, trigger=bot.user, event_type=event, details=traceback.format_exc())
    except:
        pass
    
bot.i18n.load('locale')
bot.load_extensions('cogs')
bot.load_extension('jishaku')
task = bot.loop.create_task(initDatabase())
bot.run(cfg.get_token())
