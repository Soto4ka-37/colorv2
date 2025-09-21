import disnake
from datetime import datetime
from disnake.ext import commands
from exceptions import ColorFormateException, DownloadAvatarException, CanNotInteractWithBotException
from modules.config import cfg

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def handle_error(self, target, error: Exception):
        '''Универсальная обертка для обработки ошибок'''
        unknown_error = False
        emoji = cfg.CROSS_EMOJI
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"Отсутствует обязательный аргумент: `{error.param.name}`."
        elif isinstance(error, commands.MemberNotFound):
            message = "Указанный пользователь не найден."
        elif isinstance(error, commands.BotMissingPermissions):
            missing = ', '.join(error.missing_permissions)
            message = f"У бота недостаточно прав: `{missing}`."
        elif isinstance(error, commands.MissingPermissions):
            missing = ', '.join(error.missing_permissions)
            message = f"У вас недостаточно прав: `{missing}`."
        elif isinstance(error, commands.CommandOnCooldown):
            message = f"Не так часто! Попробуйте снова через `{round(error.retry_after, 2)}` секунд."
            emoji = cfg.TIMER_EMOJI
        elif isinstance(error, commands.CommandInvokeError):
            error = error.original
            if isinstance(error, ColorFormateException):
                message = f'Неверный формат цвета! Воспользуйтесь командой **</color help:1327037046778364026>** для подробной информации.'
            elif isinstance(error, DownloadAvatarException):
                message = str(error)
            elif isinstance(error, CanNotInteractWithBotException):
                message = str(error)
            else:
                message = f"Произошла ошибка: `{str(error)}`"
                unknown_error = True
                
        elif isinstance(error, commands.NotOwner):
            message = "Только владелец бота может использовать эту команду."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "Эту команду нельзя использовать в личных сообщениях."
        else:
            message = f"Непредвиденная ошибка: `{str(error)}`"
            unknown_error = True
            
        embed = disnake.Embed(
            title='Что-то пошло не так...',
            description=f"{emoji} {message}", 
            color=cfg.ERROR_COLOR,
            timestamp=datetime.now()
        )

        # ------------------------
        # Определяем, что за объект target
        # ------------------------
        try:
            if isinstance(target, disnake.Interaction):
                # Интеракция
                if target.response.is_done():
                    await target.channel.send(embed=embed)
                else:
                    await target.response.send_message(embed=embed)
            else:
                # ctx команды
                await target.send(embed=embed, view=None)
        except disnake.NotFound:
            if hasattr(target, "channel"):
                await target.channel.send(embed=embed)

        if unknown_error:
            raise error

    @commands.Cog.listener('on_command_error')
    async def on_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    @commands.Cog.listener('on_slash_command_error')
    async def on_slash_command_error(self, inter, error):
        await self.handle_error(inter, error)


def setup(bot):
    bot.add_cog(Errors(bot))
