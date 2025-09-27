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
        if not message.guild:
            return
        if message.guild.id == 1168297956663906376 or message.guild.id == 1193355299512406021:
            n = random.randint(1, 35)
            if n == 9:
                n = random.randint(1, 13)
                if n in [1,2,3,4]:
                    await addReaction(message, '✅')
                elif n in [5,6,7]:
                    await addReaction(message, '😏')
                elif n in [8,9]:
                    await message.channel.send('@еверуоне')
                elif n in [10,11]:
                    await message.channel.send('✅')
                elif n in [12]:
                    await message.guild.me.edit(nick='хуёчек')
                    await message.channel.send(f'{message.guild.me.mention} 😏')
                elif n in [13]:
                    await message.channel.send('кагда рдк? 🧐')
            if 'роблокс' in message.content.lower():
                await message.reply('РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ')
            if 'рдк' in message.content.lower():
                await message.reply('<@511936410551451668> кОгДа рДк? 😏')
            if '@everyone' in message.content.lower():
                await message.channel.send('@еверуоне')

    @commands.is_owner()
    @commands.command('clg')
    async def clg(self, ctx: commands.Context, guild_id: int, channel_id: int):
        embed = disnake.Embed(
            title="Бот был обновлён",
            description=(
                "**Ченджлог 2.0.1**\n"
                "- Исправлена ошибка зацикливания автоответчика модуля режоктирования\n"
                "**Ченджлог 2.1.0**\n"
                "- Улучшена структура кода\n"
                "- Оптимизированы компоненты `ConfirmView` и `ColorChoiseView` для выбора цвета\n"
                "- Обновлён компонент для работы с сообщениями `UniversalUiMessage`\n"
                "- Убраны лишние загрузочные сообщения\n"
                "- Переработан компонент `AutoPaginatorView` который используется в команде **</settings access list:1414915966839820370>**\n"
                "- Обновлён модуль режоктирования\n"
                "- Добавлен статус аналогично версии `1.X.X`"
            ),
            color=cfg.MAIN_COLOR
        )
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        await channel.send(embed=embed)
        
def setup(bot):
    bot.add_cog(SmapRejactirovanie(bot))
