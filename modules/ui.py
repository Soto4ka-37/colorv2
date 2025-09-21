import disnake
import asyncio
import enum
import time

from disnake.ext import commands
from typing import Literal, Self

from modules.config import cfg
from modules.colorFunctions import Color

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
    async def init(self, ctx: disnake.Interaction | commands.Context, embed: disnake.Embed, view: disnake.ui.View = None) -> Self:
        """Функция отправки первого сообщения"""
        if isinstance(ctx, disnake.Interaction):
            await ctx.response.send_message(embed=embed)
            self.message = await ctx.original_message()
            self.owner = ctx.author
            
            return self
        elif isinstance(ctx, commands.Context):
            try:
                self.message = await ctx.reply(embed=embed)
            except:
                self.message = await ctx.send(embed=embed)
            self.owner = ctx.author
            return self
        else:
            raise ValueError('Неверный тип данных в UniversalUiMessage()')
        
    async def edit(self, embed: disnake.Embed, view: disnake.ui.View = None) -> Self:
        """Основная функция отправки сообщений"""
        try:
            self.message = await self.message.edit(embed=embed, view=view)
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
        
    async def clearImages(self) -> Self:
        """Удаляет изображения из прошлой итерации, которые не чистятся дискордом"""
        if self.message.embeds:
            embed = self.message.embeds[0]
            new_embed = disnake.Embed.from_dict(embed.to_dict())
            new_embed.set_image(url=None)
            self.message = await self.message.edit(embed=new_embed, attachments=[])
            return self
        else:
            self.message = await self.message.edit(attachments=[])
            return self
        
class TextPaginatorView(disnake.ui.View):
    def __init__(self, ui: UniversalUiMessage, text: str, per_page: int = 4000):
        super().__init__(timeout=120)
        self.ui = ui
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
        embed = disnake.Embed(description=self.pages[self.page])
        embed.set_footer(text=f"Страница {self.page+1}/{len(self.pages)}")
        if inter:
            await inter.response.edit_message(embed=embed, view=self)
        else:
            await self.ui.edit(embed=embed, view=self)

    @disnake.ui.button(emoji="⬅️", style=disnake.ButtonStyle.gray)
    async def prev(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        if self.page > 0:
            self.page -= 1
            await self.show_page(inter)

    @disnake.ui.button(emoji="➡️", style=disnake.ButtonStyle.gray)
    async def next(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
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
        for item in self.children:
            item.disabled = True
        timeout_embed = disnake.Embed(
            title="Подтверждение устарело",
            description=f"{cfg.TIMER_EMOJI} Время взаимодействия вышло!",
            color=cfg.ERROR_COLOR
        )
        timeout_embed.set_image(url=None)
        try:
            await self.ui.edit(embed=timeout_embed, view=self)
        except Exception:
            pass
        self.value = None
        self._event.set()
        self.stop()

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = True
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = False
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()

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
        for item in self.children:
            item.disabled = True
        timeout_embed = disnake.Embed(
            title='Выбор устарел',
            description=f"{cfg.TIMER_EMOJI} Время взаимодействия вышло!",
            color=cfg.ERROR_COLOR
        )
        timeout_embed.set_image(url=None)
        try:
            await self.ui.edit(embed=timeout_embed, view=self)
        except Exception:
            pass
        self.value = None
        self._event.set()
        self.stop()

        
    @disnake.ui.button(label="1", style=disnake.ButtonStyle.blurple)
    async def color1(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = self.colors[0]
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()
    @disnake.ui.button(label="2", style=disnake.ButtonStyle.blurple)
    async def color2(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = self.colors[1]
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()
        
    @disnake.ui.button(label="3", style=disnake.ButtonStyle.blurple)
    async def color3(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = self.colors[2]
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()      

    @disnake.ui.button(label="4", style=disnake.ButtonStyle.blurple)
    async def color4(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = self.colors[3]
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()
        
    @disnake.ui.button(label="5", style=disnake.ButtonStyle.blurple)
    async def color5(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = self.colors[4]
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()
        
    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.Interaction):
        if inter.author.id != self.ui.owner.id:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title='Что-то пошло не так...',
                    description=f"{cfg.BARRIER_EMOJI} Это не ваше взаимодействие.",
                    color=cfg.ERROR_COLOR
                ),
                ephemeral=True
            )
            return
        self.value = False
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(
            view=self
        )
        self._event.set()
        self.stop()
        
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