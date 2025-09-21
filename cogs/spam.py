import disnake
import random
from disnake.ext import commands
from modules.config import cfg

async def addReaction(message: disnake.Message, reaction: str):
    try:
        await message.add_reaction(reaction)
    except:
        pass
class SmapRejactirovanie(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener('on_message')
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if message.guild.id == 1168297956663906376:
            if random.randint(1, 150) == 1:
                await addReaction(message, '✅')
            if random.randint(1, 150) == 1:
                await addReaction(message, '😏')
            if random.randint(1, 150) == 1:
                await addReaction(message, cfg.CHECKMARK_EMOJI)
                
            if 'роблокс' in message.content.lower():
                await message.reply('РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ')
            if 'рдк' in message.content.lower():
                await message.reply('<@511936410551451668> кОгДа рДк? 😏')
            
def setup(bot):
    bot.add_cog(SmapRejactirovanie(bot))
