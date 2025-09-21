import disnake
import asyncio
from disnake.ext import commands
from modules.ui import UniversalUiMessage, ConfirmView, ColorChoiseView
from modules.discordFunctions import checkBotPermissions, generateRole, removeUserRoles, moveRole
from modules.colorFunctions import randomColor, Color
from modules.imageFunctions import generateColorImage, getDominantColors, generateFiveColorsImage
from cogs.settingsCommand import checkMemberAccess
from exceptions import CanNotInteractWithBotException
from modules.ui import cd
from modules.config import cfg

async def processHelp(ui: UniversalUiMessage) -> None:
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

async def processReset(ui: UniversalUiMessage, member: disnake.Member, need_message: bool = True) -> None:
    '''Функция для выполнения команды сброса'''
    failed = await removeUserRoles(member.guild, member.id)
    if failed:
        roles = ', '.join(f'<@&{role_id}>' for role_id in failed)
        embed = disnake.Embed(
            title='Предупреждение',
            description=f'{cfg.WARNING_EMOJI} Не удалось удалить следующие роли: {roles}. Пожалуйста, удалите их вручную или свяжитесь с администратором сервера.',
            color=cfg.ERROR_COLOR
        )
        await ui.sendChild(embed)
    
    embed = disnake.Embed(
        title='Успех',
        description=(
            f'{cfg.CHECKMARK_EMOJI} Ваш цвет успешно сброшен.'
            if ui.owner.id == member.id
            else f"{cfg.CHECKMARK_EMOJI} Цвет учатника `{member}` успешно сброшен."
        ),
        color=cfg.MAIN_COLOR)
    if need_message:
        await ui.edit(embed)
    
async def processColor(ui: UniversalUiMessage, member: disnake.Member, color: Color) -> None:
    '''Функция для выполнения смены цвета'''
    # Проверяем кулдаун на создание цвета
    cdwn = cd.check(ui.owner.id, cd.t.COLOR, 10)
    if cdwn:
        embed = disnake.Embed(
            title='Не торопись ты так 😮‍💨',
            description=(
                f'{cfg.TIMER_EMOJI} Один цвет раз в 10 секунд. Подтверждение не просто так придумано.\n'
                f'Кстати осталось ещё `{cdwn}` секунд.'
            ),
            color=cfg.ERROR_COLOR
        )
        await ui.edit(embed)
        return
    
    embed = disnake.Embed(
        description=f'{cfg.LOADING_EMOJI} Создаю цвет...',
        color=cfg.MAIN_COLOR
    )
    await ui.edit(embed)
    # Удаляем все старые роли
    await processReset(ui, member, False)
    
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
    
async def processAvatar(ui: UniversalUiMessage, member: disnake.Member, color: Color):
    colors = await getDominantColors(member)
    # Проверяем белый список
    if not await checkMemberAccess(ui.owner):
        embed = disnake.Embed(
            title="Что-то пошло не так..",
            description=f'{cfg.BARRIER_EMOJI} Только пользователи с определёнными ролями могут менять свой цвет!',
            color=cfg.MAIN_COLOR
        )
        await ui.edit(embed)
        return
    # Цикл выбора и подтверждения
    while True:
        # Предоставляем выбор из 5 цветов
        embed = disnake.Embed(
            title="Анализ аватарки",
            description=f"{cfg.QUESTION_EMOJI} Выберите цвет из списка ниже:"
        )
        image = await generateFiveColorsImage(colors)

        embed.set_image(file=disnake.File(image, filename='colors.webp'))
        view = ColorChoiseView(ui, colors)
        await ui.edit(embed, view)

        # Ждём выбора
        color = await view.wait()
        await ui.clearImages()
        
        if color is None:
            return  # Таймаут
        elif color is False:
            embed = disnake.Embed(
                title="Отмена",
                description=f'{cfg.CROSS_EMOJI} Отменено пользователем.',
                color=cfg.ERROR_COLOR
            )
            await ui.edit(embed)
            return  # Отмена пользователем
        
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
        await ui.clearImages()
        if result is None:
            return
        if result is True:
            break
        # если result == False то цикл повторится

    # Выполняем процесс создания цвета с таймаутом 7 секунд
    try:
        await asyncio.wait_for(processColor(ui, member, color), timeout=7)
    except asyncio.TimeoutError:
        embed = disnake.Embed(
            title='Что-то пошло не так..',
            description=f'{cfg.TIMER_EMOJI} Процесс создания цвета занял слишком много времени и был аварийно завершен.',
            color=cfg.ERROR_COLOR
        )
        await ui.edit(embed)
    return

async def autocompleteCheckColorValid(inter, string: str) -> list[str]:
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
        # Проверяем права бота
        await checkBotPermissions(ctx.guild)

        if hex_color not in [None, 'помощь', 'help', '?']:
            # Проверяем права на изменение чужих ролей
            if member not in [None, ctx.author]:
                if not ctx.author.guild_permissions.manage_roles:
                    raise commands.MissingPermissions(['manage_roles'])
            if not member:
                member = ctx.author
            
            if member.bot:
                raise CanNotInteractWithBotException(f"Боты не могут иметь цвета.")
        
        embed = disnake.Embed(
            description=f'{cfg.LOADING_EMOJI} Пожалуйста подождите...',
            color=cfg.MAIN_COLOR
        )
        ui = UniversalUiMessage()
        await ui.init(ctx, embed)
        
        try:
            # Сброс цвета
            if hex_color in ['сброс', 'reset', '-']:
                # Подтверждение сброса цвета
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
                wait = await view.wait()
                await ui.clearImages()
                if wait is None:
                    return
                if wait == False:
                    embed = disnake.Embed(
                        title='Отмена',
                        description=f'{cfg.CROSS_EMOJI} Отменено пользователем.',
                        color=cfg.ERROR_COLOR
                    )
                    return await ui.edit(embed=embed)
                
                # Сброс цвета
                return await processReset(ui, member)
            # Случайный цвет
            if hex_color in ['случайный', 'рандом', 'random']:
                color = randomColor()
            # Анализ аватарки
            elif hex_color in ['аватар', 'avatar', 'аватарка']:
                return await processAvatar(ui, member, hex_color)
            # Помощь
            elif hex_color in [None, 'помощь', 'help', '?']:
                return await processHelp(ui)
            else:
                color = Color(hex_color)
                
            # Проверяем белый список
            if not await checkMemberAccess(ui.owner):
                embed = disnake.Embed(
                    title="Что-то пошло не так..",
                    description=f'{cfg.BARRIER_EMOJI} Только пользователи с определёнными ролями могут менять свой цвет!',
                    color=cfg.MAIN_COLOR
                )
                await ui.edit(embed)
                return
            # Подтверждение выбора цвета
            color_name, percent = await color.getName()
            embed = disnake.Embed(
                title=f'{color_name.upper()} ({percent})',
                description=(
                    f'{cfg.QUESTION_EMOJI} Вы действительно хотите установить этот цвет?'
                    if ui.owner.id == member.id
                    else f'{cfg.QUESTION_EMOJI} Вы действительно хотите установить этот цвет для участника `{member}`?'
                ),
                color=color.disnakeColor)
            embed.set_image(file=disnake.File(await generateColorImage(color), filename=f'{color.text}.webp'))
            view = ConfirmView(ui)
            await ui.edit(embed, view)
            wait = await view.wait()
            await ui.clearImages()
            if wait is None:
                return
            if wait == False:
                embed = disnake.Embed(
                    title='Отмена',
                    description=f'{cfg.CROSS_EMOJI} Отменено пользователем.',
                    color=cfg.ERROR_COLOR
                )
                return await ui.edit(embed)
            # Выполняем процесс создания цвета с таймаутом 7 секунд
            try:
                await asyncio.wait_for(processColor(ui, member, color), timeout=7)
            except asyncio.TimeoutError:
                embed = disnake.Embed(
                    title='Что-то пошло не так..',
                    description=f'{cfg.TIMER_EMOJI} Процесс создания цвета занял слишком много времени и был аварийно завершен.',
                    color=cfg.ERROR_COLOR
                )
                return await ui.edit(embed)
        except Exception as e:
            await ui.message.delete()
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

