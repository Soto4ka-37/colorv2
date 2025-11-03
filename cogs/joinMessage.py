import disnake
from disnake.ext import commands
from modules.config import cfg
from modules.emojis import emoji

JOIN_EMBED = disnake.Embed(
    description=(
        '# 👋 Спасибо что добавили бота на сервер!\n'
        f'## {emoji.KEY} Для корреткной работы нужны следующие права:\n'
        f'- `читать сообщения` (`read_messages`)\n'
        f'- `отправлять сообщения` (`send_messages`)\n'
        f'- `прикреплять файлы` (`embed_links`)\n'
        f'- `управлять ролями` (`manage_roles`)\n'
        '\n'
        f'## {emoji.GEAR} Настройка\n'
        'По умолчанию **все участники** сервера (Даже если их роль выше бота) имеют право менять цвет.\n'
        'Вы можете ограничить использование добавив роли в белый список **</settings access add:1414915966839820370>**.\n'
        '\n'
        f'## {emoji.HELP} Использование\n'
        'Для помощи по функционалу бота напишите **</color help:1327037046778364026>**\n'
        '-# Бот написан [soto4ka37](https://soto4ka37.ru) для **Режоктирования** в 2025 году.\n'
        '-# Открытый исходный код на доступен [GitHub](https://github.com/Soto4ka-37/colorv2).'
    ),
    color=cfg.MAIN_COLOR
)

class JoinMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self, guild: disnake.Guild):
        for channel in guild.channels:
            if channel.name in ['chat', 'general', 'main', 'чат', 'основной', '💬чат-не-путать-с-чад'] and channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(embed=JOIN_EMBED)
                    return
                except:
                    continue
                
        for channel in guild.channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(embed=JOIN_EMBED)
                    return
                except:
                    continue
                

    @commands.command('send-wlcm')
    async def test(self, ctx: commands.Context):
        channel = ctx.channel
        await channel.send(embed=JOIN_EMBED)
        return
            
def setup(bot):
    bot.add_cog(JoinMessage(bot))
