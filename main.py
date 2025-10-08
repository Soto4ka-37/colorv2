import disnake
import traceback
from disnake.ext import commands

from modules.config import cfg
from modules.database import initDatabase

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), owner_id=cfg.OWNER, help_command=None)

@bot.event
async def on_ready():
    print(f'Авторизован как {bot.user}')    
    
bot.i18n.load('locale')
bot.load_extensions('cogs')
bot.load_extension('jishaku')
task = bot.loop.create_task(initDatabase())
bot.run(cfg.get_token())
