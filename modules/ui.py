import disnake
import asyncio
import enum
import time

from disnake.ext import commands
from typing import Literal, Self

from modules.config import cfg
from modules.emojis import emoji
from modules.colorFunctions import Color

# !!! Класс для работы с сообщениями !!!
class UniversalUiMessage():
    def __init__(self):
        '''Класс для работы с сообщениями
        Требует init() (Асинхронно)
        Свойства:
        - message: актуальное сообщение интерфейса
        - owner: пользователь вызвавший интерфейс

        '''
        self.message = None
        self.owner = None
        self.guild = None
        self.ctx = None
        
    async def init(self, ctx: disnake.Interaction | commands.Context, embed: disnake.Embed = None, view: disnake.ui.View = None) -> Self:
        """Функция инициализации интерфейса. Отправка сообщения опциональна. """
        self.ctx = ctx
        self.guild = ctx.guild
        self.owner = ctx.author
        if embed: # С сообщением
            await self._send(embed, view)
        return self
    
    async def _send(self, embed: disnake.Embed, view: disnake.ui.View = None) -> Self:
        """Функция отправки первого сообщения"""
        if isinstance(self.ctx, disnake.Interaction):
            if view:
                await self.ctx.send(embed=embed, view=view)
            else:
                await self.ctx.send(embed=embed)
            self.message = await self.ctx.original_message()
        elif isinstance(self.ctx, commands.Context):
            try:
                if view:
                    self.message = await self.ctx.reply(embed=embed, view=view)
                else:
                    self.message = await self.ctx.reply(embed=embed)
            except:
                if view:
                    self.message = await self.ctx.send(embed=embed, view=view)
                else:
                    self.message = await self.ctx.send(embed=embed)
                
    async def edit(self, embed: disnake.Embed, view: disnake.ui.View = None) -> Self:
        """Основная функция отправки сообщений"""
        if not self.ctx:
            raise Exception("UniversalUiMessage не инициализирован. Вызовите init() перед использованием.")
        elif not self.message:
            await self._send(embed, view)
            return self
        try:
            self.message = await self.message.edit(embed=embed, view=view, attachments=[])
            return self
        except disnake.Forbidden:
            raise commands.BotMissingPermissions(['embed_links'])
        except disnake.HTTPException:
            self.message = await self.message.channel.send(embed=embed, view=view)
            return self
        
    async def sendChild(self, embed: disnake.Embed, view: disnake.ui.View = None) -> disnake.Message:
        try:
            return await self.message.reply(embed=embed, view=view)
        except disnake.Forbidden:
            raise commands.BotMissingPermissions(['embed_links'])
        except disnake.HTTPException:
            return await self.message.channel.send(embed=embed, view=view)
        
    async def delete(self) -> None:
        """Удаляет сообщение"""
        if self.message:
            try:
                await self.message.delete()
            except:
                pass
            self.message = None
        
# !!! Частые сообщения !!!
async def sendNotYour(ui: UniversalUiMessage, inter: disnake.Interaction):
    """Отправляет сообщение что это не ваше взаимодействие"""
    await inter.send(
        ephemeral=True,
        embed=disnake.Embed(
            description=f"{emoji.FORBIDDEN} Это взаимодейсвтие пренадлежит {ui.owner.mention}.",
            color=cfg.ERROR_COLOR
        )
    )
    
# !!! Компоненты View с кнопками !!! 
class AutoPaginatorView(disnake.ui.View):
    def __init__(self, ui: UniversalUiMessage, title: str, text: str, per_page: int = 4000):
        super().__init__(timeout=120)
        self.ui = ui
        self.title = title
        self.pages = self._split_text(text, per_page)
        self.page = 0
        self._event = asyncio.Event()

    def _split_text(self, text: str, per_page: int) -> list[str]:
        lines = text.split('\n')
        pages = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 <= per_page:
                current += (('\n' if current else '') + line)
            else:
                if current:
                    pages.append(current)
                if len(line) > per_page:
                    words = line.split(' ')
                    chunk = ""
                    for word in words:
                        if len(chunk) + len(word) + 1 <= per_page:
                            chunk += ((' ' if chunk else '') + word)
                        else:
                            if chunk:
                                pages.append(chunk)
                            chunk = word
                    if chunk:
                        pages.append(chunk)
                else:
                    current = line
        if current:
            pages.append(current)
        return pages if pages else [""]

    async def show_page(self, inter: disnake.Interaction = None):
        embed = disnake.Embed(
            title=self.title,
            description=self.pages[self.page],
            color=cfg.MAIN_COLOR
        )

        if len(self.pages) > 1:
            if self.page == 0:
                self.children[0].disabled = True
            if self.page == len(self.pages) - 1:
                self.children[1].disabled = True
            embed.set_footer(text=f"Страница {self.page+1} из {len(self.pages)}")
        else:
            self.stop()
            self.children = []
                
        if inter:
            await inter.response.edit_message(embed=embed, view=self)
        else:
            await self.ui.edit(embed=embed, view=self)

    @disnake.ui.button(emoji=emoji.LEFT_ARROW, style=disnake.ButtonStyle.gray)
    async def prev(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)
            return
        if self.page > 0:
            self.page -= 1
            await self.show_page(inter)

    @disnake.ui.button(emoji=emoji.RIGHT_ARROW, style=disnake.ButtonStyle.gray)
    async def next(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)
            return
        if self.page < len(self.pages) - 1:
            self.page += 1
            await self.show_page(inter)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.ui.edit(view=self)
        except Exception:
            pass
        self._event.set()
        self.stop()
    
class ConfirmView(disnake.ui.View):
    def __init__(self, ui: UniversalUiMessage, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.ui = ui
        self.value: bool = False
        self._event = asyncio.Event()
        
    async def wait(self) -> bool | None:
        """Асинхронно ждём нажатия кнопки или таймаут."""
        await self._event.wait()
        return self.value
    
    async def on_timeout(self):
        """Вызывается, когда View устарела."""
        self.value = None
        self._event.set()
        self.stop()

    @disnake.ui.button(emoji=emoji.CHECKMARK, label="Продолжить", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = True
        self._event.set()
        self.stop()
        await inter.response.defer()
        
    @disnake.ui.button(emoji=emoji.CROSS, label="Отмена", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = False
        self._event.set()
        self.stop()
        await inter.response.defer()

class ColorChoiseView(disnake.ui.View):
    def __init__(self, ui: UniversalUiMessage, colors: list[Color]):
        super().__init__(timeout=60)
        self.ui = ui
        self.value: Color | None | Literal[False] = None
        self._event = asyncio.Event()
        self.colors = colors
        
    async def wait(self) -> Color | None:
        """Асинхронно ждём нажатия кнопки или таймаут."""
        await self._event.wait()
        return self.value
    
    async def on_timeout(self):
        """Вызывается, когда View устарела."""
        self.value = None
        self._event.set()
        self.stop()

        
    @disnake.ui.button(label="1", style=disnake.ButtonStyle.blurple)
    async def color1(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = self.colors[0]
        self._event.set()
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(label="2", style=disnake.ButtonStyle.blurple)
    async def color2(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = self.colors[1]
        self._event.set()
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(label="3", style=disnake.ButtonStyle.blurple)
    async def color3(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = self.colors[2]
        self._event.set()
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(label="4", style=disnake.ButtonStyle.blurple)
    async def color4(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = self.colors[3]
        self._event.set()
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(label="5", style=disnake.ButtonStyle.blurple)
    async def color5(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = self.colors[4]
        self._event.set()
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(emoji=emoji.CROSS, label="Отмена", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await sendNotYour(self.ui, inter)

        self.value = False
        self._event.set()
        self.stop()
    
# !!! Кулдауны !!!
    
class CooldownType(enum.Enum):
    COLOR = enum.auto()

class CooldownManager:
    def __init__(self):
        # {CooldownType: {user_id: expire_timestamp}}
        self._cooldowns: dict[CooldownType, dict[int, float]] = {}
        self.t = CooldownType
    def _cleanup_user(self, user_id: int, cd_type: CooldownType) -> None:
        """Удаляет просроченные кулдауны для конкретного пользователя."""
        user_cds = self._cooldowns.get(cd_type)
        if not user_cds:
            return

        expire = user_cds.get(user_id)
        if expire is not None and expire <= time.time():
            user_cds.pop(user_id, None)
            if not user_cds:
                self._cooldowns.pop(cd_type, None)

    def set_cooldown(self, user_id: int, cd_type: CooldownType, seconds: int) -> None:
        """Ставит кулдаун пользователю."""
        expire_time = time.time() + seconds
        self._cooldowns.setdefault(cd_type, {})[user_id] = expire_time

    def get_remaining(self, user_id: int, cd_type: CooldownType) -> float:
        """Возвращает оставшееся время кулдауна в секундах, либо 0 если кулдаун неактивен."""
        self._cleanup_user(user_id, cd_type)
        expire = self._cooldowns.get(cd_type, {}).get(user_id)
        if expire is None:
            return 0
        return max(0, int(expire - time.time()))

    def check(self, user_id: int, cd_type: CooldownType, seconds: int) -> int | Literal[0]:
        """
        Проверяет и ставит кулдаун, возвращает натуральное число: 0 - нет куладуна

        """
        cooldown = self.get_remaining(user_id, cd_type)
        if cooldown > 0:
            return cooldown
        
        self.set_cooldown(user_id, cd_type, seconds)
        return 0

cd = CooldownManager()