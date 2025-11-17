# МОДУЛЬ РЕЖОКТИРОВАНИЯ
# ЭТОТ ФАЙЛ НЕ ОБЯЗАТЕЛЬНЫЙ ДЛЯ РАБОТЫ БОТА И ЯВЛЯЕТСЯ ШУТКОЙ
# ВЫ МОЖЕТЕ ЕГО УДАЛИТЬ
# СОБЫТИЯ РАБОТАЮТ ТОЛЬКО НА СЕРВЕРЕ РЕЖОКТИРОВАНИЯ
# МОГУТ ПРИСУТСТВОВАТЬ ОСКОРБИТЕЛЬНЫЕ ИЛИ НЕЦЕНЗУРНЫЕ ВЫРАЖЕНИЯ
import disnake
import random
import aiohttp
import bs4
import datetime
import asyncio
from disnake.ext import commands
from modules.config import cfg
from modules.emojis import emoji

class AnekdotEvent():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.runned = False
        self.channel = None
            
    async def getAnekdot(self):
        url = 'https://anekdot.ru/random/anekdot'
        headers = {"User-Agent": "Firefox"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                web = await response.text()

        bs = bs4.BeautifulSoup(web, "lxml")
        result = str(bs.find_all(class_="topicbox")[1].find(class_="text"))
        text = result.replace("br/", "\n")
        text = text.split(">")
        text[0] = ""
        text = ''.join(text)
        text = text.split("<")
        text[-1] = ""
        text = ''.join(text)
        return text
    
    # Каждый день
    async def init(self):
        if self.runned:
            return
        await self.bot.wait_until_ready()
        try:
            self.channel = await self.bot.fetch_channel(1437149222851055656)
        except Exception as e:
            return
        self.runned = True
        
        if self.channel:
            await self.channel.send(embed=disnake.Embed(description=f'{emoji.WARNING} Бот был перезапущен. Пересоздаю событие в этом чате...', color=cfg.MAIN_COLOR))
            while True:
                now = datetime.datetime.now(datetime.timezone.utc)
                try:
                    anekdot = await self.getAnekdot()
                        
                    # Время до след дня
                    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                    next = (tomorrow - now).total_seconds()
                    
                    message = await self.channel.send(embed=disnake.Embed(description=f'# Смешнявка 🤣🤣😂🤣💀🤣\n```\n{anekdot}```\n**Следующий: <t:{int(tomorrow.timestamp())}:R>**',color=cfg.MAIN_COLOR))
                    try:
                        await message.add_reaction('✅')
                        await message.add_reaction('🤣')
                        await message.add_reaction('💀')
                    except Exception as e:
                        pass
                    await asyncio.sleep(next)
                except Exception as e:
                    await asyncio.sleep(10)
                    continue
            
class BaseAction():
    async def activate(self, message: disnake.Message):
        '''Выполняемое действие'''
        pass
    
class MessageAction(BaseAction):
    '''Дейсвтие отправки сообщения'''
    def __init__(self, message: str):
        self.message = message
        
    async def activate(self, message: disnake.Message):
        '''Активировать действие'''
        try:
            await message.reply(self.message, mention_author=False)
        except:
            await message.channel.send(self.message)
        
class ReactionAction(BaseAction):
    '''Дейсвтие добавления реакции'''
    def __init__(self, reaction: str):
        self.reaction = reaction
        
    async def activate(self, message: disnake.Message):
        '''Активировать действие'''
        try:
            await message.add_reaction(self.reaction)
        except:
            pass
        
class Event:
    '''Событие, состоящее из нескольких действий'''
    def __init__(self):
        self.actions: list[BaseAction] = []
        
    def addAction(self, action: BaseAction):
        '''Добавить действие в событие'''
        self.actions.append(action)
        
    async def activate(self, message: disnake.Message):
        '''Активировать событие'''
        for action in self.actions:
            await action.activate(message)

class Trigger(Event):
    '''Событие вызываемое по триггеру (Одной или нескольким строкам)'''
    def __init__(self, *trigger_srings: str):
        self.trigger_srings = trigger_srings
        
        super().__init__()
        
    async def checkActivate(self, message: disnake.Message):
        '''Проверить сообщение на активацию триггера'''
        content = message.content.lower()
        for trigger_str in self.trigger_srings:
            if trigger_str.lower() in content:
                await self.activate(message)
                return

class RandomTrigger(Trigger):
    '''Событие вызываемое по триггеру, но выбирающее случайное действие с указаным шансом'''
    def __init__(self, *trigger_srings):
        super().__init__(*trigger_srings)
        self.total_chance = 0
        self.actions: list[tuple[BaseAction, int]] = []
    
    def addAction(self, action: BaseAction, chance: int):
        '''Добавить действие с указанным шансом'''
        self.actions.append((action, chance))
        self.total_chance += chance
        
    async def activate(self, message: disnake.Message):
        '''Активировать событие'''
        rand = random.randint(1, self.total_chance)
        current = 0
        for action, chance in self.actions:
            current += chance
            if rand <= current:
                await action.activate(message)
                return
    
class EventManager():
    '''Модуль управления событиями'''
    def __init__(self):
        self.events: list[tuple[Event, int]] = []
        self.triggers: list[Trigger] = []
        self.total_chance = 0
        
    def addEvent(self, event: Event, chance: int = 1):
        '''Добавить событие с указанным шансом'''
        if chance < 1:
            raise ValueError('Шанс должен быть больше 0')
        
        if isinstance(event, Trigger):
            self.triggers.append(event)
            
        elif isinstance(event, Event):
            self.events.append((event, chance))
            self.total_chance += chance
        else:
            raise TypeError('Событие должно быть объектом Event или Trigger')
        
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
        if self.total_chance == 0:
            return
        
        rand = random.randint(1, 35)
        if rand == 22:
            await self.activateRandomEvent(message)
            
    async def checkTriggers(self, message: disnake.Message):
        '''Проверить триггеры'''
        for trigger in self.triggers:
            await trigger.checkActivate(message)

class RejactirovanieCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.em = EventManager()
        self.ae = AnekdotEvent(bot)
        self.bot.loop.create_task(self.initEvents())
        self.bot.loop.create_task(self.ae.init())

    async def initEvents(self):
        await self.bot.wait_until_ready()
        if not self.bot.get_guild(1168297956663906376):
            return
        
        em = self.em

        # События по триггеру
        trigger = RandomTrigger('@everyone')
        trigger.addAction(MessageAction('@еверуоне'), 2)
        trigger.addAction(MessageAction('да щаебал свои еверуоне слать урож'), 1)
        em.addEvent(trigger)

        trigger = Trigger('режоктирование')
        trigger.addAction(MessageAction('Воистину режоктирование'))
        em.addEvent(trigger)

        trigger = Trigger('рдк')
        trigger.addAction(MessageAction('<@511936410551451668> кОгДа рДк? 😏'))
        em.addEvent(trigger)

        trigger = Trigger('роблокс')
        trigger.addAction(MessageAction('РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ'))
        em.addEvent(trigger)

        trigger = Trigger('яблоко', '<@906829390472675350>')
        trigger.addAction(MessageAction('**⚠️ПРЕДУПРЕЖДЕНИЕ⚠️**\n@яблоко❤1488 признан экстремисткой террористической организацией в этом дискорд сообществе'))
        em.addEvent(trigger)

        # Случайные события
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

        event = Event()
        event.addAction(MessageAction('спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жиз'))
        em.addEvent(event, 1)
    
    @commands.Cog.listener('on_message')
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.guild.id == 1168297956663906376 or message.guild.id == 1193355299512406021:
            await self.em.randomCallback(message)
            await self.em.checkTriggers(message)
            
    @commands.is_owner()
    @commands.command('clg')
    async def clg(self, ctx: commands.Context, channel_id: int = None):
        if channel_id is not None:
            channel = await self.bot.fetch_channel(channel_id)
        else:
            channel = ctx.channel
            
        embed = disnake.Embed(
            description=(
                f"**{emoji.GEAR} Ченджлог v2.3.2**\n"
                "- Добавлены события `Trigger` и `RandomTrigger` в модуль режоктирования\n"
                "- Действие `MessageAction` модуля режактирования теперь отвечает на сообщение\n"
                "- Исправление некоторых ошибок\n"
            ),
            color=cfg.MAIN_COLOR
        )
        
        await channel.send(embed=embed)
        
def setup(bot):
    bot.add_cog(RejactirovanieCog(bot))
