import disnake
import asyncio
from disnake.ext import commands
from modules.ui import UniversalUiMessage, ConfirmView, ColorChoiseView
from modules.discordFunctions import checkBotPermissions, generateRole, removeUserRoles, moveRole
from modules.colorFunctions import randomColor, Color
from modules.imageFunctions import generateColorImage, getDominantColors, generateFiveColorsImage
from cogs.settingsCommand import checkMemberAccess
from modules.ui import cd
from modules.config import cfg
from modules.emojis import emoji
from modules.database import colorTable
from typing import Literal

async def sendHelp(ui: UniversalUiMessage) -> None:
    '''Справка по использованию команды color'''
    embed = disnake.Embed(
        description=(            
            f"# {emoji.HELP} Справка по использованию бота\n"
            'Поля помеченные `[*]` являются обязательными. Использовать цель могут только участники с правом `manage_roles`.\n'
            
            f'### {emoji.PAINT} Смена цвета\n'
            'Устанавливает указанный цвет, в формате `HEX`\n'
            'Команды: </color create:1327037046778364026> или `!цвет` или `!color` (`!colour`)\n'
            'Поля: `[*HEX]`, `[@цель]`\n'
            
            f'### {emoji.DICE} Случайный цвет\n'
            'Генерирует и устанавливает случайный цвет\n'
            'Команды: </color random:1327037046778364026> или `!цвет рандом` или `!color random`\n'
            'Поля: `[@цель]`\n'

            f'### {emoji.LOUPE} Анализ аватара\n'
            'Предлагает цвета на основе аватарки\n'
            'Команды: </color avatar:1327037046778364026> или `!цвет аватар`\n'
            'Поля: `[@источник]`\n'

            f'### {emoji.SHIELD} Восстановление цвета\n'
            'Пересоздаёт ваш текущий цвет\n'
            'Команды: </color repair:1327037046778364026> или `!цвет починить`\n'
            'Поля: `[@цель]`\n'

            f'### {emoji.HAMMER} Сброс цвета\n'
            'Удаляет текущий цвет\n'
            'Команды: </color reset:1327037046778364026> или `!цвет -` или `!цвет сброс` или `!color reset`\n'
            'Поля: `[@цель]`\n'

            f'### {emoji.CHAT} Взаимодействия\n'
            'ПКМ по пользователю -> Приложения:\n'
            '- Скопировать цвет роли\n'
            '- Скопировать цвет аватара\n'

            f'### {emoji.INFO} О формате HEX\n'
            'Формат: `#RRGGBB` (Например: `#FFA500` или `ff0000`)\n'
            '[Выбрать цвет с помощью палитры](https://csscolor.ru/)\n'
            '[Таблица цветов](https://colorswall.com/ru/colors/xkcd)\n'

            f'### {emoji.CLOCK} Ограничения\n'
            '- Один участник может менять свой цвет не чаще, чем раз в 10 секунд\n'
            
            f'# {emoji.GEAR} Настройки\n'
            f'Использовать эти команды могут участники с правом `manage_roles`.\n'
            
            f'### {emoji.KEY} Белый список\n'
            'По умолчанию **отключён**, чтобы включить нужно добавить хотя бы одну роль. Люди без ролей в белом списке не смогут использовать бота\n'
            '- </settings access list:1414915966839820370> - список ролей в белом списке\n'
            '- </settings access add:1425581992619278349> `[*роль]` - добавить роль в белый список\n'
            '- </settings access remove:1425581992619278349> `[*роль]` - убрать роль из белого списка'
        ),
        color=cfg.MAIN_COLOR
    )
    await ui.edit(embed)
    
async def sendTimeout(ui: UniversalUiMessage) -> None:
    '''Сообщение о таймауте'''
    embed = disnake.Embed(
        description=f'{emoji.CLOCK} Взаимодействие оставалось без ответа слишком долго!',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)
    
async def sendNotColor(ui: UniversalUiMessage) -> None:
    '''Сообщение об отсутствии цвета у участника'''
    embed = disnake.Embed(
        description=f'{emoji.CROSS} У вас нет цвета! Создать его вы можете командой </color create:1327037046778364026>',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)

async def sendNotManageRoles(ui: UniversalUiMessage) -> None:
    '''Сообщение об отсутствии цвета у участника'''
    embed = disnake.Embed(
        description=f'{emoji.CROSS} Что бы редактировать цвет других участников необходимо право `manage_roles`!',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)
    
async def sendTooMany(ui: UniversalUiMessage) -> None:
    '''Сообщение об отсутствии цвета у участника'''
    embed = disnake.Embed(
        description=f'{emoji.CROSS} У вас нет цвета. Создать вы его можете командой </color create:1327037046778364026>',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)

async def sendCancel(ui: UniversalUiMessage) -> None:
    '''Сообщение об отмене'''
    embed = disnake.Embed(
        description=f'{emoji.CROSS} Действие отменено пользователем.',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)
    
async def sendIsBot(ui: UniversalUiMessage) -> None:
    '''Сообщение о том, что участник - бот'''
    embed = disnake.Embed(
        description=f'{emoji.CROSS} Нельзя менять цвет ботам.',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)

async def sendNotInWhitelist(ui: UniversalUiMessage) -> None:
    '''Сообщение о том, что участник не в белом списке'''
    embed = disnake.Embed(
        description=f'{emoji.FORBIDDEN} Только пользователи с определёнными ролями могут менять свой цвет!',
        color=cfg.MAIN_COLOR
    )
    await ui.edit(embed)

async def acceptColor(ui: UniversalUiMessage, member: disnake.Member, color: Color) -> bool:
    '''Функция для подтверждения выбранного цвета. Возвращает True если пользователь подтвердил выбор, False если отменил и None при таймауте'''
    # Спрашиваем подтверждение выбранного цвета
    color_name, percent = await color.getName()
    embed = disnake.Embed(
        description=(
            (
                f'## {emoji.PAINT} {color_name.upper()} ({percent})\n'
                f'Вы уверены что хотите установить этот цвет?'
            )
            if ui.owner.id == member.id
            else (
                f'## {emoji.PAINT} {color_name.upper()} ({percent})\n'
                f'Вы уверены что хотите установить этот цвет участнику `{member.name}` ({member.mention})?'
            )
        ),
        color=color.disnakeColor)
    
    embed.set_thumbnail(file=disnake.File(await generateColorImage(color), filename=f'{color.text}.webp'))

    view = ConfirmView(ui)
    await ui.edit(embed, view)

    # Ждём ответа
    result = await view.wait()
    
    return result

async def acceptReset(ui: UniversalUiMessage, member: disnake.Member) -> bool:
    '''Функция для подтверждения сброса цвета. Возвращает True если пользователь подтвердил выбор, False если отменил и None при таймауте'''
    # Спрашиваем подтверждение сброса цвета
    embed = disnake.Embed(
        description=(
            (
                f'## {emoji.HAMMER} Внимание!\n'
                'Это действие удалит ваш цвет!'
            )
            if ui.owner.id == member.id
            else (
                f'## {emoji.HAMMER} Внимание!\n'
                f'Это действие удалит цвет участника `{member.name}` ({member.mention})!'
            )
        ),
        color=cfg.ERROR_COLOR
    )
    view = ConfirmView(ui)
    await ui.edit(embed, view)

    # Ждём ответа
    result = await view.wait()
        
    return result

async def choiseAndAcceptColor(ui: UniversalUiMessage, member: disnake.Member, colors: list[Color]) -> Color | Literal[False] | None:
    '''Функция для выбора и подтверждения цвета из списка. Возвращает выбранный цвет, False если отменил и None при таймауте'''
    for _ in range(5): # Максимум 5 попыток выбора цвета
        embed = disnake.Embed(
            description=(
                f"## {emoji.LOUPE} Анализ завершён!\n"
                "Выберите цвет чтобы продолжить."
            ),
            color=cfg.MAIN_COLOR
        )
        image = await generateFiveColorsImage(colors)

        embed.set_image(file=disnake.File(image, filename='colors.webp'))

        view = ColorChoiseView(ui, colors)
        await ui.edit(embed, view)

        # Пользователь выбирает цвет
        color = await view.wait()
        # await ui.clearImages()
        
        if color is None:
            return None  # Таймаут
        elif color is False:
            return False # Отмена
        
        # Подтверждаем выбор
        result = await acceptColor(ui, member, color)
        if result is None: # Таймаут
            return None
        if result is True: # Подтверждено
            return color
        if result == False: # Повторный выбор
            continue
    return None  # Таймаут после 5 попыток выбора

async def resetColor(ui: UniversalUiMessage, member: disnake.Member) -> None:
    '''Функция для выполнения сброса цвета'''
    failed = await removeUserRoles(member.guild, member.id)
    if failed:
        roles = ', '.join(f'<@&{role_id}>' for role_id in failed)
        embed = disnake.Embed(
            description=f'{emoji.ERROR} Не удалось удалить следующие роли: {roles}. Пожалуйста, удалите их вручную или свяжитесь с администратором сервера.',
            color=cfg.ERROR_COLOR
        )
        await ui.sendChild(embed)
    
async def changeColor(ui: UniversalUiMessage, member: disnake.Member, color: Color) -> None:
    '''Функция для выполнения смены цвета'''
    # Удаляем все старые роли
    await resetColor(ui, member)
    
    # Создаём новую роль
    new_role = await generateRole(member, color)
    
    # Перемещаем роль
    warnings = await moveRole(member, new_role)

    # Выводим предупреждения, если есть
    for warning in warnings:
        embed = disnake.Embed(
            description=f'{emoji.ERROR} {warning}',
            color=cfg.ERROR_COLOR
        )
        await ui.sendChild(embed)
    
    # Выдаём роль
    await member.add_roles(new_role, reason='Выдача персональной роли цвета')
    # Отправляем сообщение об успехе
    color_name, percent = await color.getName()
    embed = disnake.Embed(
        description=(
            (
                f'# {emoji.PAINT} {color_name.upper()} ({percent})\n'
                f'{emoji.CHECKMARK} Ваш цвет успешно создан и выдан.'
            )
            if ui.owner.id == member.id
            else (
                f'# {emoji.PAINT} {color_name.upper()} ({percent})\n'
                f'{emoji.CHECKMARK} Цвет успешно создан и выдан участнику `{member.name}` ({member.mention}).'
            )
        ),
        color=color.disnakeColor
    )
    embed.set_thumbnail(file=disnake.File(await generateColorImage(color), filename=f'{color.text}.webp'))
    await ui.edit(embed)
    
async def processResetCommand(ui: UniversalUiMessage, member: disnake.Member):
    '''Процесс выполнения подкокоманды сброса цвета. Ничего не возвращает'''
    result = await acceptReset(ui, member)
    if result is None:
        return await sendTimeout(ui)
    if result is False:
        return await sendCancel(ui)
    await resetColor(ui, member)
    embed = disnake.Embed(
        description=(
            f'{emoji.CHECKMARK} Ваш цвет успешно сброшен.'
            if ui.owner.id == member.id
            else f"{emoji.CHECKMARK} Цвет учатника `{member}` успешно сброшен."
        ),
        color=cfg.MAIN_COLOR)
    await ui.edit(embed)

async def processRepairCommand(ui: UniversalUiMessage, member: disnake.Member) -> Color | None:
    color = await colorTable.getLastByUser(ui.guild.id, member.id)
    if not color:
        await sendNotColor(ui)
        return 
    return color.color

async def processAvatarCommand(ui: UniversalUiMessage, member: disnake.Member) -> Color | None:
    '''Процесс выполнения подкоманды анализа аватара. Возвращает выбранный цвет или None при ошибке'''
    await ui.edit(embed=disnake.Embed(
        description=f'{emoji.LOADING} Смотрю аватарку...',
        color=cfg.MAIN_COLOR
    ))
    # Получаем 5 доминантных цветов
    colors = await getDominantColors(member, 5)
    if not colors:
        embed = disnake.Embed(
            description=f'{emoji.ERROR} Не удалось проанализировать аватарку участника.',
            color=cfg.ERROR_COLOR
        )
        await ui.edit(embed)
        return None
    
    # Выбираем и подтверждаем цвет
    color = await choiseAndAcceptColor(ui, ui.owner, colors)
    if color is None:
        await sendTimeout(ui)
        return None
    if color is False:
        await sendCancel(ui)
        return None
    return color

async def processColorCommand(ui: UniversalUiMessage, member: disnake.Member, hex_color: str) -> Color | None:
    '''Процесс выполнения подкоманды создания цвета по коду. Возвращает выбранный цвет или None при ошибке'''
    color = Color(hex_color)
    result = await acceptColor(ui, member, color)
    if result is None:
        return await sendTimeout(ui)
    if result is False:
        return await sendCancel(ui)
    return color

async def processRandomCommand(ui: UniversalUiMessage, member: disnake.Member) -> Color | None:
    '''Процесс выполнения подкоманды случайного цвета. Возвращает созданный цвет или None при ошибке'''
    color = randomColor()
    result = await acceptColor(ui, member, color)
    if result is None:
        return await sendTimeout(ui)
    if result is False:
        return await sendCancel(ui)
    return color

async def autocompleteCheckColorValid(inter, string: str) -> list[str]:
    '''Автодополнение для проверки валидности цвета. Возвращает список с HEX кодом или сообщением об ошибке'''
    try:
        color = Color(string)
    except:
        return ['❌ Неверный формат цвета']
    return [color.hex]

class ColorCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Используется для выполнения процесса команды цвет текстового формата
    async def processColorUniversal(self, ctx: commands.Context | disnake.ApplicationCommandInteraction, hex_color: str, member: disnake.Member = None):
        '''Универсальная обёртка для цвета. Принимает команды сброс, случайный и т.д.'''
        try:
            # При помощи пропускаем в любом случае
            ui = UniversalUiMessage()
            await ui.init(ctx)
            if hex_color in [None, 'помощь', 'help', '?']:
                return await sendHelp(ui)
            # Проверяем права бота
            await checkBotPermissions(ctx.guild)

            # Проверяем белый список
            if not await checkMemberAccess(ctx.author):
                await sendNotInWhitelist(ui)
                return
                
            if not member:
                member = ctx.author
                
            if member.bot: # Нельзя менять цвет ботам
                await sendIsBot(ui)
                return
            
            # Если цель другой участник и нет прав на управление ролями
            if member != ctx.author \
            and not await self.bot.is_owner(ui.owner) \
            and hex_color not in ['аватар', 'avatar', 'аватарка'] \
            and not ctx.author.guild_permissions.manage_roles:
                raise commands.MissingPermissions(['manage_roles'])

                
            # Сброс цвета
            if hex_color in ['сброс', 'reset', '-']:
                await processResetCommand(ui, member)
                return
        
            # Случайный цвет
            elif hex_color in ['случайный', 'рандом', 'random']:
                color = await processRandomCommand(ui, member)
                
            # Анализ аватарки
            elif hex_color in ['аватар', 'avatar', 'аватарка']:
                color = await processAvatarCommand(ui, member)
                member = ctx.author
                
            elif hex_color in ['починить', 'repair', 'восстановить']:
                color = await processRepairCommand(ui, member)
            # Цвет указан
            else:
                color = await processColorCommand(ui, member, hex_color)
                
            if color is None:
                return  # Ошибка уже обработана
            
            # Проверяем кулдаун на создание цвета
            cdwn = cd.check(ui.owner.id, cd.t.COLOR, 10)
            if cdwn:
                embed = disnake.Embed(
                    description=f'{emoji.CLOCK} Вы меняете цвет слишком быстро! Подождите ещё `{cdwn}` секунд.',
                    color=cfg.ERROR_COLOR
                )
                await ui.edit(embed)
                return
            
            # # Сообщение загрузки
            embed = disnake.Embed(
                description=f'{emoji.LOADING} Применяю цвет...',
                color=cfg.MAIN_COLOR
            )
            await ui.edit(embed)  

            try:
                await asyncio.wait_for(changeColor(ui, member, color), timeout=7)
            except asyncio.TimeoutError:
                embed = disnake.Embed(
                    description=f'{emoji.ERROR} Процесс создания цвета занял слишком много времени и был аварийно завершен.',
                    color=cfg.ERROR_COLOR
                )
                return await ui.edit(embed)
        except Exception as e:
            await ui.delete()
            raise e
    
    # Текстовые события команды цвет
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name='цвет')
    async def color_ru_ctx(self, ctx: commands.Context, hex_color: str = None, member: disnake.Member = None):
        await self.processColorUniversal(ctx, hex_color, member)
        
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name='color')
    async def color_en1_ctx(self, ctx: commands.Context, hex_color: str = None, member: disnake.Member = None):
        await self.processColorUniversal(ctx, hex_color, member)
    
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name='colour')
    async def color_en1_ctx(self, ctx: commands.Context, hex_color: str = None, member: disnake.Member = None):
        await self.processColorUniversal(ctx, hex_color, member)
        
    # Интеракционные события команды цвет, разделены на субкоманды
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.guild_only()
    @commands.slash_command(name=disnake.Localized('color', key='COLOR_NAME'))
    async def color_inter(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # Создать цвет
    @color_inter.sub_command(
        name=disnake.Localized('create', key='CREATE_NAME'),
        description='Создаёт роль согласно заданному цвету'
    )
    async def color_inter_create(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hex_color: str = commands.Param(
            name=disnake.Localized('color', key='COLOR_NAME'),
            description="HEX-код цвета",
            autocomplete=autocompleteCheckColorValid
        ),
        member: disnake.Member = commands.Param(
            name=disnake.Localized('member', key='MEMBER_NAME'),
            description="Пользователь, которому выдать цвет (по умолчанию вы)",
            default=None,
        )
    ):
        await self.processColorUniversal(inter, hex_color, member)

    # Помощь
    @color_inter.sub_command(
        name=disnake.Localized('help', key='HELP_NAME'),
        description='Возвращает справку по использованию бота'
    )
    async def color_inter_help(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        await self.processColorUniversal(inter, 'help', inter.author)
    # Случайный цвет
    @color_inter.sub_command(
        name=disnake.Localized('random', key='RANDOM_NAME'),
        description='Создаёт роль со случайным цветом'
    )
    async def color_inter_random(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name=disnake.Localized('member', key='MEMBER_NAME'),
            description="Пользователь, которому выдать цвет (по умолчанию вы)",
            default=None,
        )
    ):
        await self.processColorUniversal(inter, 'random', member)

    # Цвет по аватарке
    @color_inter.sub_command(
        name=disnake.Localized('avatar', key='AVATAR_NAME'),
        description='Создаёт роль с цветом, основанным на вашем аватаре'
    )
    async def color_inter_avatar(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name=disnake.Localized('member', key='MEMBER_NAME'),
            description="Пользователь, которому выдать цвет (по умолчанию вы)",
            default=None,
        )
    ):
        await self.processColorUniversal(inter, 'avatar', member)

    # Цвет по аватарке
    @color_inter.sub_command(
        name=disnake.Localized('repair', key='REPAIR_NAME'),
        description='Восстанавливает ваш цвет из базы данных, если он был поврежден'
    )
    async def color_inter_repair(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name=disnake.Localized('member', key='MEMBER_NAME'),
            description="Пользователь, которому починить цвет (по умолчанию вы)",
            default=None,
        )
    ):
        await self.processColorUniversal(inter, 'repair', member)
        
    # Сброс цвета
    @color_inter.sub_command(
        name=disnake.Localized('reset', key='RESET_NAME'),
        description='Сбрасывает ваш цвет'
    )
    async def color_inter_reset(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            name=disnake.Localized('member', key='MEMBER_NAME'),
            description="Пользователь, которому сбросить цвет (по умолчанию вы)",
            default=None,
        )    ):
        await self.processColorUniversal(inter, 'reset', member)
        
    @commands.user_command(name='Скопировать цвет аватарки')
    async def copy_avatar(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        if not inter.guild:
            embed = disnake.Embed(
                description=f'Как ты вообще умудрился вызвать эту интеракцию в личных сообщениях?',
                color=cfg.ERROR_COLOR
            )
            await inter.send(embed=embed, ephemeral=True)
        await inter.response.defer()
        await self.processColorUniversal(inter, 'аватар', user)
        
    @commands.user_command(name='Скопировать цвет роли')
    async def copy_role(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member):
        if not inter.guild:
            embed = disnake.Embed(
                description=f'Как ты вообще умудрился вызвать эту интеракцию в личных сообщениях?',
                color=cfg.ERROR_COLOR
            )
            await inter.send(embed=embed, ephemeral=True)
        await inter.response.defer()
        await self.processColorUniversal(inter, f"{user.color.value:06x}", user)

def setup(bot: commands.Bot):
    bot.add_cog(ColorCommand(bot))

