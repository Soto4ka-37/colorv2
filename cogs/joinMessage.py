import disnake
from disnake.ext import commands
from modules.config import cfg


JOIN_EMBED = disnake.Embed(
    description=(
        '## 👋 Спасибо что пригласили бота на сервер!\n'
        'Перед началом использования бот требует следующих прав:\n'
        f'- {cfg.WARNING_EMOJI} **Перемещение роли на верхнюю позицию (см. вложение)**\n'
        f'- {cfg.EDIT_ROLE_EMOJI} Право `управлять ролями` (`manage_roles`)\n'
        f'- {cfg.EYE_EMOJI} Право `читать сообщения` (`read_messages`)\n'
        f'- {cfg.PEN_EMOJI} Право `отправлять сообщения` (`send_messages`)\n'
        f'- {cfg.IMAGE_EMOJI} Право `встраивать ссылки` (`embed_links`)\n'
        '\n'
        f'## {cfg.GEAR_EMOJI} Настройка\n'
        'По умолчанию **все участники** сервера (Даже если их роль выше бота) имеют право менять цвет.\n'
        'Вы можете ограничить использование добавив роли в белый список **</settings access add:1414667181026705498>**.\n'
        '\n'
        f'## {cfg.HELP_EMOJI} Использование\n'
        'Для помощи по функционалу бота напишите **</color help:1327037046778364026>**'
    ),
    color=cfg.MAIN_COLOR
).set_image(url='https://cdn.discordapp.com/attachments/1193356261606035516/1414641875947880468/1757347304423.gif')

class JoinMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self, guild: disnake.Guild):
        soto4ka37 = await self.bot.fetch_user(747936027049721946)
        JOIN_EMBED.set_footer(text='💜 Разработано soto4ka37 специально для режокирования', icon_url=(soto4ka37.avatar or soto4ka37.default_avatar).url)
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
        soto4ka37 = await self.bot.fetch_user(747936027049721946)
        JOIN_EMBED.set_footer(text='💜 Разработано soto4ka37 специально для режокирования', icon_url=(soto4ka37.avatar or soto4ka37.default_avatar).url)
        await channel.send(embed=JOIN_EMBED)
        return
            
def setup(bot):
    bot.add_cog(JoinMessage(bot))
