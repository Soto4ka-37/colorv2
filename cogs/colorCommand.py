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
from typing import Literal

async def sendHelp(ui: UniversalUiMessage) -> None:
    '''Справка по использованию команды color'''
    embed = disnake.Embed(
        title=f"{cfg.HELP_EMOJI} Справка по использованию бота",
        description=(
            "Команда позволяет создавать персональные цветовые роли.\n"
            f"Все команды кроме справки поддерживают использование на другом участнике.\n\n"
            f"**Список команд:**\n"
            f"- </color create:1327037046778364026> `(!цвет)` `[*HEX]` — создать цвет по коду\n"
            f"- </color random:1327037046778364026> `(!цвет рандом)` — случайный цвет\n"
            f"- </color avatar:1327037046778364026> `(!цвет аватар)` — цвет на основе аватарки\n"
            f"- </color reset:1327037046778364026> `(!цвет -)` — сбросить цвет\n"
            f"- </color help:1327037046778364026> `(!цвет ?)` — открыть эту справку\n\n"
            f"**О формате HEX:**\n"
            "Вид `#RRGGBB` (Например `#FFA500` или `ff0000`)\nВы можете [выбрать цвет](https://csscolor.ru/) или воспользоваться [таблицей](https://colorswall.com/ru/colors/xkcd).\n\n"
            f"**Ограничения:**\n"
            f"- {cfg.TIMER_EMOJI} Один участник может менять свой цвет раз в 10 секунд\n"
        ),
        color=cfg.MAIN_COLOR
    )
    await ui.edit(embed)
    
async def sendTimeout(ui: UniversalUiMessage) -> None:
    '''Сообщение о таймауте'''
    embed = disnake.Embed(
        title='Что-то пошло не так..',
        description=f'{cfg.TIMER_EMOJI} Время ожидания ответа истекло. Пожалуйста, попробуйте снова.',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)
    
async def sendCancel(ui: UniversalUiMessage) -> None:
    '''Сообщение об отмене'''
    embed = disnake.Embed(
        title='Отмена',
        description=f'{cfg.CROSS_EMOJI} Отменено пользователем.',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)
    
async def sendIsBot(ui: UniversalUiMessage) -> None:
    '''Сообщение о том, что участник - бот'''
    embed = disnake.Embed(
        title='Что-то пошло не так..',
        description=f'{cfg.CROSS_EMOJI} Нельзя менять цвет ботам.',
        color=cfg.ERROR_COLOR
    )
    await ui.edit(embed)

async def sendNotInWhitelist(ui: UniversalUiMessage) -> None:
    '''Сообщение о том, что участник не в белом списке'''
    embed = disnake.Embed(
        title="Что-то пошло не так..",
        description=f'{cfg.BARRIER_EMOJI} Только пользователи с определёнными ролями могут менять свой цвет!',
        color=cfg.MAIN_COLOR
    )
    await ui.edit(embed)

async def acceptColor(ui: UniversalUiMessage, member: disnake.Member, color: Color) -> bool:
    '''Функция для подтверждения выбранного цвета. Возвращает True если пользователь подтвердил выбор, False если отменил и None при таймауте'''
    # Спрашиваем подтверждение выбранного цвета
    color_name, percent = await color.getName()
    embed = disnake.Embed(
        title=f'{color_name.upper()} ({percent})',
        description=(
            f'{cfg.QUESTION_EMOJI} Вы действительно хотите установить этот цвет?'
            if ui.owner.id == member.id
            else f'{cfg.QUESTION_EMOJI} Вы действительно хотите установить этот цвет для участника `{member}`?'
        ),
        color=color.disnakeColor)
    
    embed.set_thumbnail(file=disnake.File(await generateColorImage(color), filename=f'{color.text}.webp'))

    view = ConfirmView(ui)
    await ui.edit(embed, view)

    # Ждём ответа
    result = await view.wait()
    # await ui.clearImages()
    
    return result

async def acceptReset(ui: UniversalUiMessage, member: disnake.Member) -> bool:
    '''Функция для подтверждения сброса цвета. Возвращает True если пользователь подтвердил выбор, False если отменил и None при таймауте'''
    # Спрашиваем подтверждение сброса цвета
    embed = disnake.Embed(
        title="Сброс",
        description=(
            f'{cfg.QUESTION_EMOJI} Вы действительно хотите удалить свой цвет?'
            if ui.owner.id == member.id
            else f'{cfg.QUESTION_EMOJI} Вы действительно хотите удалить цвет участника `{member}`?'
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
            title="Анализ аватарки",
            description=f"{cfg.QUESTION_EMOJI} Выберите цвет из списка ниже:",
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
            title='Предупреждение',
            description=f'{cfg.WARNING_EMOJI} Не удалось удалить следующие роли: {roles}. Пожалуйста, удалите их вручную или свяжитесь с администратором сервера.',
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
            description=f'{cfg.WARNING_EMOJI} {warning}',
            color=cfg.ERROR_COLOR
        )
        await ui.sendChild(embed)
    
    # Выдаём роль
    await member.add_roles(new_role, reason='Выдача персональной роли цвета')
    # Отправляем сообщение об успехе
    color_name, percent = await color.getName()
    embed = disnake.Embed(
        title=f'{color_name.upper()} ({percent})',
        description=(
            f'{cfg.CHECKMARK_EMOJI} Цвет успешно создан и выдан вам.'
            if ui.owner.id == member.id
            else f'{cfg.CHECKMARK_EMOJI} Цвет успешно создан и выдан участнику `{member}`.'
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
        title='Успех',
        description=(
            f'{cfg.CHECKMARK_EMOJI} Ваш цвет успешно сброшен.'
            if ui.owner.id == member.id
            else f"{cfg.CHECKMARK_EMOJI} Цвет учатника `{member}` успешно сброшен."
        ),
        color=cfg.MAIN_COLOR)
    await ui.edit(embed)

async def processAvatarCommand(ui: UniversalUiMessage, member: disnake.Member) -> Color | None:
    '''Процесс выполнения подкоманды анализа аватара. Возвращает выбранный цвет или None при ошибке'''
    
    # embed = disnake.Embed(
    #     description=f'{cfg.LOADING_EMOJI} Анализирую аватарку...',
    #     color=cfg.MAIN_COLOR
    # )
    # await ui.edit(embed)
    
    # Получаем 5 доминантных цветов
    colors = await getDominantColors(member, 5)
    if not colors:
        embed = disnake.Embed(
            title='Что-то пошло не так..',
            description=f'{cfg.CROSS_EMOJI} Не удалось проанализировать аватарку участника.',
            color=cfg.ERROR_COLOR
        )
        await ui.edit(embed)
        return None
    
    # Выбираем и подтверждаем цвет
    color = await choiseAndAcceptColor(ui, member, colors)
    if color is None:
        await sendTimeout(ui)
        return None
    if color is False:
        await sendCancel(ui)
        return None
    return color

async def processColorCommand(ui: UniversalUiMessage, member: disnake.Member, hex_color: str) -> None:
    '''Процесс выполнения подкоманды создания цвета по коду. Возвращает выбранный цвет или None при ошибке'''
    color = Color(hex_color)
    result = await acceptColor(ui, member, color)
    if result is None:
        return await sendTimeout(ui)
    if result is False:
        return await sendCancel(ui)
    return color

async def processRandomCommand(ui: UniversalUiMessage, member: disnake.Member) -> Color:
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

            # Проверяем права на изменение чужих ролей, если участник указан
            if member not in [None, ctx.author]:
                if not ctx.author.guild_permissions.manage_roles:
                    raise commands.MissingPermissions(['manage_roles'])
                if member.bot: # Нельзя менять цвет ботам
                    embed = disnake.Embed(
                        title='Что-то пошло не так..',
                        description=f'{cfg.CROSS_EMOJI} Нельзя менять цвет ботам.',
                        color=cfg.ERROR_COLOR
                    )
                    return await ui.edit(embed)
            # Если участник не указан, то меняем цвет себе
            else: 
                member = ctx.author
                
            # Проверяем белый список
            if not await checkMemberAccess(ctx.author):
                await sendNotInWhitelist(ui)
                return
            
            # !!! ОБРАБОТКА ПОДКОММАНД !!!
            # Сброс цвета
            if hex_color in ['сброс', 'reset', '-']:
                await processResetCommand(ui, member)
                return
        
            # Случайный цвет
            if hex_color in ['случайный', 'рандом', 'random']:
                color = await processRandomCommand(ui, member)
            # Анализ аватарки
            elif hex_color in ['аватар', 'avatar', 'аватарка']:
                color = await processAvatarCommand(ui, member)
            # Цвет указан
            else:
                color = await processColorCommand(ui, member, hex_color)
                
            if color is None:
                return  # Ошибка уже обработана
            
            # Проверяем кулдаун на создание цвета
            cdwn = cd.check(ui.owner.id, cd.t.COLOR, 10)
            if cdwn:
                embed = disnake.Embed(
                    title='Не торопись ты так 😮‍💨',
                    description=(
                        f'{cfg.TIMER_EMOJI} Один цвет раз в 10 секунд.\n'
                        f'Подождите ещё `{cdwn}` секунд.'
                    ),
                    color=cfg.ERROR_COLOR
                )
                await ui.edit(embed)
                return
            
            # # Сообщение загрузки
            embed = disnake.Embed(
                description=f'{cfg.LOADING_EMOJI} Применяю цвет...',
                color=cfg.MAIN_COLOR
            )
            await ui.edit(embed)  

            try:
                await asyncio.wait_for(changeColor(ui, member, color), timeout=7)
            except asyncio.TimeoutError:
                embed = disnake.Embed(
                    title='Что-то пошло не так..',
                    description=f'{cfg.TIMER_EMOJI} Процесс создания цвета занял слишком много времени и был аварийно завершен.',
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
def setup(bot: commands.Bot):
    bot.add_cog(ColorCommand(bot))

