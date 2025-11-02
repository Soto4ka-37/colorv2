import disnake
import random
from disnake.ext import commands
from modules.config import cfg
from modules.emojis import emoji

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
                n = random.randint(1, 65)
                if n in range(1,11):
                    await addReaction(message, '✅')
                elif n in range(11,21):
                    await addReaction(message, '😏')
                elif n in range(21, 26):
                    await message.channel.send('@еверуоне')
                elif n in range(26, 31):
                    await message.channel.send('✅')
                elif n in range(31, 33):
                    await message.guild.me.edit(nick='хуёчек')
                    await message.channel.send(f'{message.guild.me.mention} 😏')
                elif n in range(33, 36):
                    await message.channel.send('кагда рдк? 🧐')
                elif n in range(36, 38):
                    await message.channel.send('"курсед пижорас"')
                elif n in range(38, 41):
                    await message.channel.send('снят.')
                elif n in range(41, 45):
                    await message.channel.send('режоктирование')
                elif n in range(45, 51):
                    await addReaction(message, '😭')
                elif n in range(51, 56):
                    await message.channel.send('я никогда не промахиваюсь')
                elif n in range(56, 61):
                    await message.channel.send('нэы')
                elif n in range(61,66):
                    await message.channel.send('ржкт глв мзг :smirk::disguised_face::flushed::sob::thinking::pleading_face::white_check_mark:\n — 0:30\n@ржкт глв мзг :smirk::disguised_face::flushed::sob::thinking::pleading_face::white_check_mark: ситошка не спамь!')
            if 'роблокс' in message.content.lower():
                await message.reply('РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ')
            if 'рдк' in message.content.lower():
                await message.reply('<@511936410551451668> кОгДа рДк? 😏')
            if '<@906829390472675350>' in message.content or 'яблоко' in message.content.lower():
                await message.reply('Well well  well 卐 ᛋᛋ\nБОТ\n\n — 19:06\n**⚠️ПРЕДУПРЕЖДЕНИЕ⚠️\n <@906829390472675350> признан экстремисткой террористической организацией в этом дискорд сообществе')
            if '@everyone' in message.content.lower():
                n = random.randint(1, 3)
                if n in range(1,3):
                    await message.channel.send('@еверуоне')
                else:
                    await message.channel.send('да щаебал со своим everyone урож')


    @commands.is_owner()
    @commands.command('clg')
    async def clg(self, ctx: commands.Context, channel_id: int = None):
        if channel_id is not None:
            channel = await self.bot.fetch_channel(channel_id)
        else:
            channel = ctx.channel
            
        embed = disnake.Embed(
            description=(
                f"**{emoji.INFO} Ченджлог v2.3**\n"
                "- Иконки перенесены с `config.json` в `emojis.json`"
                "- Обновлён набор иконок и основной цвет.\n"
                "- Обновлена стилистика сообщений, убраны заголовки из эмбедов."
                "- Добавлен генератор config.json (Подготовка к OpenSource)"
            ),
            color=cfg.MAIN_COLOR
        )
        
        await channel.send(embed=embed)
        
def setup(bot):
    bot.add_cog(SmapRejactirovanie(bot))
