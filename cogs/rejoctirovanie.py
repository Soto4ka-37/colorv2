# МОДУЛЬ РЕЖОКТИРОВАНИЯ
# ЭТОТ ФАЙЛ НЕ ОБЯЗАТЕЛЬНЫЙ ДЛЯ РАБОТЫ БОТА И ЯВЛЯЕТСЯ ШУТКОЙ
# ВЫ МОЖЕТЕ ЕГО УДАЛИТЬ
# СОБЫТИЯ РАБОТАЮТ ТОЛЬКО НА СЕРВЕРЕ РЕЖОКТИРОВАНИЯ
import disnake
import random
from disnake.ext import commands
from modules.config import cfg
from modules.emojis import emoji

class BaseAction():
    async def activate(self, message: disnake.Message):
        '''Выполняемое действие'''
        pass
    
class MessageAction(BaseAction):
    '''Дейсвтие отправки сообщения'''
    def __init__(self, message: str):
        self.message = message
        
    async def activate(self, message: disnake.Message):
        await message.channel.send(self.message)
        
class ReactionAction(BaseAction):
    '''Дейсвтие добавления реакции'''
    def __init__(self, reaction: str):
        self.reaction = reaction
        
    async def activate(self, message: disnake.Message):
        try:
            await message.add_reaction(self.reaction)
        except:
            pass
        
class Event():
    '''Событие, состоящее из нескольких действий'''
    def __init__(self):
        self.actions: list[BaseAction] = []
        
    def addAction(self, action: BaseAction):
        '''Добавить действие в событие'''
        self.actions.append(action)
        
    async def activate(self, message: disnake.Message):
        for action in self.actions:
            await action.activate(message)
            
class EventManager():
    '''Модуль управления событиями'''
    def __init__(self):
        self.events: list[tuple[Event, int]] = []
        self.total_chance = 0
        
    def addEvent(self, event: Event, chance: int):
        '''Добавить событие с указанным шансом'''
        self.events.append((event, chance))
        self.total_chance += chance
    
    async def activateRandomEvent(self, message: disnake.Message):
        '''Активировать случайное событие'''
        rand = random.randint(1, self.total_chance)
        current = 0
        for event, chance in self.events:
            current += chance
            if rand <= current:
                await event.activate(message)
                return
            
    async def randomCallback(self, message: disnake.Message):
        '''Случайный вызов события с шансом 1 из 35'''
        rand = random.randint(1, 35)
        if rand == 22:
            await self.activateRandomEvent(message)
            
em = EventManager()

event = Event()
event.addAction(ReactionAction('✅'))
em.addEvent(event, 10)

event = Event()
event.addAction(ReactionAction('😏'))
em.addEvent(event, 10)

event = Event()
event.addAction(ReactionAction('😭'))
em.addEvent(event, 10)

event = Event()
event.addAction(MessageAction('@еверуоне'))
em.addEvent(event, 5)

event = Event()
event.addAction(MessageAction('✅'))
em.addEvent(event, 5)

event = Event()
event.addAction(MessageAction('кагда рдк? 🧐'))
em.addEvent(event, 1)

event = Event()
event.addAction(MessageAction('"курсед пижорас"'))
em.addEvent(event, 2)

event = Event()
event.addAction(MessageAction('снят.'))
em.addEvent(event, 3)

event = Event()
event.addAction(MessageAction('режоктирование'))
em.addEvent(event, 4)

event = Event()
event.addAction(MessageAction('я никогда не промахиваюсь'))
em.addEvent(event, 1)

event = Event()
event.addAction(MessageAction('нэы'))
em.addEvent(event, 5)

event = Event()
event.addAction(MessageAction('дооо'))
em.addEvent(event, 5)

event = Event()
event.addAction(MessageAction('ты умрешь и тд и тп'))
em.addEvent(event, 2)

event = Event()
event.addAction(MessageAction(
    '🇷🇺 zхц тыща минус семь:\n — 0:30\n'
    '@ржкт глв мзг :smirk::disguised_face::flushed::sob::thinking::pleading_face::white_check_mark: ситошка не спамь!'
))
em.addEvent(event, 2)

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
            await em.randomCallback(message)

    @commands.is_owner()
    @commands.command('clg')
    async def clg(self, ctx: commands.Context, channel_id: int = None):
        if channel_id is not None:
            channel = await self.bot.fetch_channel(channel_id)
        else:
            channel = ctx.channel
            
        embed = disnake.Embed(
            description=(
                f"**{emoji.GEAR} Ченджлог v2.3**\n"
                "- Иконки перенесены с `config.json` в `emojis.json`\n"
                "- Обновлён набор иконок и основной цвет\n"
                "- Обновлена стилистика сообщений\n"
                "- Добавлен генератор config.json (Подготовка к OpenSource)\n"
                f"**{emoji.GEAR} Ченджлог v2.3.1**\n"
                '- Открытие исходного кода на [GitHub](https://github.com/Soto4ka-37/colorv2)\n'
                '- Новый логотип и баннер\n'
                '- Переписана система случайных событий модуля режактирования\n'
                '- Исправлена очистка цвета при выходе участника с сервера\n'
                '- Создан метод очистки участников вышедших когда бот был в офлайне\n'
                '- Улучшения стилистики, добавлено больше иконок\n'
                '- Переписана справка </color help:1327037046778364026>\n'
            ),
            color=cfg.MAIN_COLOR
        )
        
        await channel.send(embed=embed)
        
def setup(bot):
    bot.add_cog(SmapRejactirovanie(bot))
