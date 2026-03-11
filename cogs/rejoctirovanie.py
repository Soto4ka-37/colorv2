# МОДУЛЬ РЕЖОКТИРОВАНИЯ
# ЭТОТ ФАЙЛ НЕ ОБЯЗАТЕЛЬНЫЙ ДЛЯ РАБОТЫ БОТА И ЯВЛЯЕТСЯ ШУТКОЙ
# ВЫ МОЖЕТЕ ЕГО УДАЛИТЬ
# СОБЫТИЯ РАБОТАЮТ ТОЛЬКО НА СЕРВЕРЕ РЕЖОКТИРОВАНИЯ
# МОГУТ ПРИСУТСТВОВАТЬ ОСКОРБИТЕЛЬНЫЕ ИЛИ НЕЦЕНЗУРНЫЕ ВЫРАЖЕНИЯ
import disnake
import random
import aiohttp
import bs4
import json
import datetime
import asyncio
from disnake.ext import commands
from modules.config import cfg
from modules.emojis import emoji
class Config():
    def __init__(self) -> None:
        self._file = 'rej_cfg.json'
        self._cfg: dict = {}

    def _getDataString(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return f'{now.day}.{now.month}.{now.year}'

    def load(self):
        try:
            with open(self._file, 'r', encoding='utf-8') as f:
                self._cfg = json.load(f)
        except FileNotFoundError:
            self._cfg = {
                'guilds': [],
                'random_messages': [],
                'anecdot': [],
                'last_anecdot': None,
                'smirk': [],
            }
            
    def save(self):
        with open(self._file, 'w', encoding='utf-8') as f:
            json.dump(self._cfg, f, indent=4, ensure_ascii=False)
    def getGuilds(self):
        return self._cfg.get('guilds', [])
    def addGuild(self, guild_id: int):
        if guild_id not in self._cfg.get('guilds', []):
            self._cfg.setdefault('guilds', []).append(guild_id)
            self.save()
    def getRandomMessages(self):
        return self._cfg.get('random_messages', [])
    def addRandomMessage(self, message: str):
        if message not in self._cfg.get('random_messages', []):
            self._cfg.setdefault('random_messages', []).append(message)
            self.save()
    def removeRandomMessage(self, message: str):
        if message in self._cfg.get('random_messages', []):
            self._cfg['random_messages'].remove(message)
            self.save()
    def removeGuild(self, guild_id: int):
        if guild_id in self._cfg.get('guilds', []):
            self._cfg['guilds'].remove(guild_id)
            self.save()
    def getAnekdotChannels(self):
        return self._cfg.get('anecdot', [])
    def addAnekdotChannel(self, channel_id: int):
        if channel_id not in self._cfg.get('anecdot', []):
            self._cfg.setdefault('anecdot', []).append(channel_id)
            self.save()
    def removeAnekdotChannel(self, channel_id: int):
        if channel_id in self._cfg.get('anecdot', []):
            self._cfg['anecdot'].remove(channel_id)
            self.save()
    def getSmirkGuilds(self):
        return self._cfg.get('smirk', [])
    def addSmirkGuild(self, guild_id: int):
        if guild_id not in self._cfg.get('smirk', []):
            self._cfg.setdefault('smirk', []).append(guild_id)
            self.save()
    def removeSmirkGuild(self, guild_id: int):
        if guild_id in self._cfg.get('smirk', []):
            self._cfg['smirk'].remove(guild_id)
            self.save()
    def setLastAnekdotDay(self):
        self._cfg['last_anecdot'] = self._getDataString()
        self.save()
    def isAnecdotAtDay(self):
        return self._cfg.get('last_anecdot') == self._getDataString()
    
cfg_rj = Config()
cfg_rj.load()

class AnekdotEveryDay():
    def __init__(self):
        self.runned = False
            
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
    
    async def start(self, bot: commands.Bot):
        if self.runned:
            return
        await bot.wait_until_ready()
        self.runned = True
        if cfg_rj.isAnecdotAtDay():
            now = datetime.datetime.now(datetime.timezone.utc)
            tomorrow = (now + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            next = (tomorrow - now).total_seconds()
            await asyncio.sleep(next)
        while True:
            for channel_id in cfg_rj.getAnekdotChannels():
                try:
                    channel = await bot.fetch_channel(channel_id)
                except disnake.NotFound:
                    continue
                now = datetime.datetime.now(datetime.timezone.utc)
                try:
                    anekdot = await self.getAnekdot()
                        
                    # Время до след дня
                    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                    next = (tomorrow - now).total_seconds()
                    
                    if not channel.permissions_for(channel.guild.me).send_messages:
                        continue
                    
                    message = await channel.send(embed=disnake.Embed(description=f'# Смешнявка 🤣🤣😂🤣💀🤣\n```\n{anekdot}```\n**Следующий: <t:{int(tomorrow.timestamp())}:R>**',color=cfg.MAIN_COLOR),
                                                        components=[disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Ещё хачу', custom_id='reroll_anekdot', emoji=emoji.DICE)])
                    try:
                        await message.add_reaction('✅')
                        await message.add_reaction('🤌')
                        await message.add_reaction('🤣')
                        await message.add_reaction('💀')
                    except Exception as e:
                        pass
                except Exception as e:
                        await asyncio.sleep(10)
                        continue

            cfg_rj.setLastAnekdotDay()
            await asyncio.sleep(next)

anekdot = AnekdotEveryDay()

class RandomMessageSender:
    def __init__(self):
        self.messages = []
        self.running = False

    def AddMessage(self, text, weight):
        self.messages.append((text, weight))

    async def start(self, bot: commands.Bot):
        if self.running:
            return
        self.running = True
        while self.running:
            wait_time = random.randint(18000, 36000)
            await asyncio.sleep(wait_time)
            
            if not self.messages:
                continue
            
            for channel_id in cfg_rj.getRandomMessages():
                try:
                    channel = await bot.fetch_channel(channel_id)
                    if not channel.permissions_for(channel.guild.me).send_messages:
                        continue
                    message = random.choices(self.messages, weights=[w for _, w in self.messages])[0][0]
                    await channel.send(message)
                except:
                    continue

    def stop(self):
        self.running = False
        
random_message_sender = RandomMessageSender()

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
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if isinstance(message, disnake.Message):
            try:
                await message.reply(self.message, mention_author=False)
            except:
                await message.channel.send(self.message)
        else:
            raise TypeError('MessageAction может быть активирован только на объекте Message')
        
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

class TriggerEvent(Event):
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

class RandomTriggerEvent(TriggerEvent):
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
        self.triggers: list[TriggerEvent] = []
        self.total_chance = 0
        
    def addEvent(self, event: Event, chance: int = 1):
        '''Добавить событие с указанным шансом'''
        if chance < 1:
            raise ValueError('Шанс должен быть больше 0')
        
        if isinstance(event, TriggerEvent):
            self.triggers.append(event)
            
        elif isinstance(event, Event):
            self.events.append((event, chance))
            self.total_chance += chance
        else:
            raise TypeError('Событие должно быть объектом Event или Trigger')
        
    async def activateRandomEvent(self, message: disnake.Message | disnake.TextChannel):
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
        self.last_reloll_anekdot = None
        self.em = EventManager()
        self.bot.loop.create_task(self.initEvents())
        self.bot.loop.create_task(anekdot.start(bot))

    async def initEvents(self):
        await self.bot.wait_until_ready()
        em = self.em

        # События по триггеру
        trigger = RandomTriggerEvent('@everyone')
        trigger.addAction(MessageAction('@еверуоне'), 2)
        trigger.addAction(MessageAction('да щаебал свои еверуоне слать урож'), 1)
        em.addEvent(trigger)

        trigger = RandomTriggerEvent('режоктирование')
        trigger.addAction(MessageAction('Воистину режоктирование'), 1)
        trigger.addAction(MessageAction('Режактирование головного мозга'), 1)
        em.addEvent(trigger)

        trigger = RandomTriggerEvent('режактирование')
        trigger.addAction(MessageAction('Воистину режактирование'), 1)
        trigger.addAction(MessageAction('Режактирование головного мозга'), 1)
        em.addEvent(trigger)

        trigger = TriggerEvent('рдк')
        trigger.addAction(MessageAction('<@511936410551451668> кОгДа рДк? 😏'))
        em.addEvent(trigger)

        trigger = TriggerEvent('роблокс')
        trigger.addAction(MessageAction('РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ РОБЛОКС ДЛЯ ИНВАЛИДОВ'))
        em.addEvent(trigger)

        # Случайные события
        event = Event()
        event.addAction(ReactionAction('✅'))
        em.addEvent(event, 3)

        event = Event()
        event.addAction(ReactionAction('😏'))
        em.addEvent(event, 3)

        event = Event()
        event.addAction(ReactionAction('😭'))
        em.addEvent(event, 3)

        event = Event()
        event.addAction(MessageAction('@еверуоне'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('✅'))
        em.addEvent(event, 2)

        event = Event()
        event.addAction(MessageAction('кагда рдк? 🧐'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('"курсед пижорас"'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('снят.'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('режоктирование'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('я никогда не промахиваюсь'))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('нэы'))
        em.addEvent(event, 2)

        event = Event()
        event.addAction(MessageAction('дооо'))
        em.addEvent(event, 2)

        event = Event()
        event.addAction(MessageAction('ты умрешь и тд и тп'))
        em.addEvent(event, 2)

        event = Event()
        event.addAction(MessageAction(
            '🇷🇺 zхц тыща минус семь:\n — 0:30\n'
            '@ржкт глв мзг :smirk::disguised_face::flushed::sob::thinking::pleading_face::white_check_mark: ситошка не спамь!'
        ))
        em.addEvent(event, 1)

        event = Event()
        event.addAction(MessageAction('спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизньспам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жизнь спам это жиз'))
        em.addEvent(event, 1)
    
        event = Event()
        event.addAction(MessageAction('Иван Маркус помним скорбим 🥀🥀🥀'))
        em.addEvent(event, 2)
        
        event = Event()
        event.addAction(MessageAction('Привет! Я - Дельфин, дружелюбный AI ассистент.\nРазвяжуся естественно и непринужденно.\nЕсли вам нужно что-то напишите, скажите \'напишите\', и я за вас напишу.\nЧеловек: Привет! Я - Дельфин, дружелюбный AI ассистент.\nРазвяжуся естественно и непринужденно.\nЕсли вам нужно что-то напишите, скажите \'напишите\', и я за вас напишу.\nТы: Привет! Я - Дельфин, дружелюбный AI ассистент.\nРазвяжуся естественно и непринужденно.\nЕсли вам нужна какая-то информация, спросите \'ответьте\'.'))
        em.addEvent(event, 1)
        
        event = Event()
        event.addAction(MessageAction('усрiсь'))
        em.addEvent(event, 1)
        
        event = Event()
        event.addAction(MessageAction('усрался'))
        em.addEvent(event, 1)
        
        event = Event()
        act = MessageAction('жоброе утро')
        event.addAction(act)
        em.addEvent(event, 2)
        
        event = Event()
        act = MessageAction('чпокойной ночи')
        event.addAction(act)
        em.addEvent(event, 2)
        event = Event()
        act = MessageAction('мурня')
        event.addAction(act)
        em.addEvent(event, 2)
        
        
        random_message_sender.AddMessage('Жоброе утро', 1)   
        random_message_sender.AddMessage('Спокойной ночи', 1)
        random_message_sender.AddMessage('Антисрактив', 1)   

        self.bot.loop.create_task(random_message_sender.start(self.bot))
        
    @commands.Cog.listener('on_button_click')
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if self.last_reloll_anekdot is not None and self.last_reloll_anekdot + datetime.timedelta(seconds=10) > datetime.datetime.now(datetime.timezone.utc):
            await inter.response.send_message(f'Один анекдот раз в 10 секунд, падажжди', ephemeral=True)
            return
        if inter.component.custom_id == 'reroll_anekdot':
            await inter.response.defer()
            message = await inter.channel.send(embed=disnake.Embed(description=f'{emoji.LOADING} Жагрузка смешнявки'))
            self.last_reloll_anekdot = datetime.datetime.now(datetime.timezone.utc)
            
            text = await anekdot.getAnekdot()
            embed = embed=disnake.Embed(description=f'# Смешнявка (Внеплановая) 🤣🤣😂🤣💀🤣\n```\n{text}```',color=cfg.MAIN_COLOR)
            embed.set_footer(icon_url=(inter.author.avatar or inter.author.default_avatar).url, text=f'Ещё хотел {inter.author.display_name}')
            await message.edit(
                embed=embed,
                components=[disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Ну ещё ещё', custom_id='reroll_anekdot', emoji=emoji.DICE)]
            )
            await message.add_reaction('✅')
            await message.add_reaction('🤌')
            await message.add_reaction('🤣')
            await message.add_reaction('💀')

    @commands.Cog.listener('on_message')
    async def on_message(self, message: disnake.Message):
        if not message.guild:
            return

        if message.guild.id in cfg_rj.getSmirkGuilds():
            try:
                await message.add_reaction("😏")
            except:
                pass
            
        if message.author.bot:
            return
        
        if message.guild.id in cfg_rj.getGuilds():
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
                f"**{emoji.GEAR} Ченджлог v2.3.9**\n"
                "- Переработан конфиг режактирования\n"
                "- Переработан модуль сообщений в случайный момент\n"
                "- Перераспределены шансы случшайных сообщений\n"
                "- Добавлен перевод неправильной раскладки `!даун`"
            ),
            color=cfg.MAIN_COLOR
        )
        
        await channel.send(embed=embed)
        
    @commands.is_owner()
    @commands.command('смирк')
    async def smirk(self, ctx: commands.Context):
        if ctx.guild.id not in cfg_rj.getSmirkGuilds():
            cfg_rj.addSmirkGuild(ctx.guild.id)
            return await ctx.send(
                embed=disnake.Embed(description=f'{emoji.CHECKMARK} СМИРКОПОКАЛИПСИКС АКТИВИРОВАН', color=cfg.MAIN_COLOR)
            )

        cfg_rj.removeSmirkGuild(ctx.guild.id)
        await ctx.send(
            embed=disnake.Embed(description=f'{emoji.CROSS} СМИРКОПОКАЛИПСИКС ДЕАКТИВИРОВАН', color=cfg.MAIN_COLOR)
        )
        
    @commands.is_owner()
    @commands.command('сообщения')
    async def random_messages(self, ctx: commands.Context):
        if ctx.channel.id not in cfg_rj.getRandomMessages():
            cfg_rj.addRandomMessage(ctx.channel.id)
            return await ctx.send(
                embed=disnake.Embed(description=f'{emoji.CHECKMARK} теперь в этом чате будут сообщения в случайный момент', color=cfg.MAIN_COLOR)
            )

        cfg_rj.removeRandomMessage(ctx.channel.id)
        await ctx.send(
            embed=disnake.Embed(description=f'{emoji.CROSS} прекращаю спам =(', color=cfg.MAIN_COLOR)
        )
        
    @commands.is_owner()
    @commands.command('режактирование')
    async def rejactirovanie(self, ctx: commands.Context):
        if ctx.guild.id not in cfg_rj.getGuilds():
            cfg_rj.addGuild(ctx.guild.id)
            return await ctx.send(
                embed=disnake.Embed(description=f'{emoji.CHECKMARK} Теперь этот сервер режактирование', color=cfg.MAIN_COLOR)
            )

        cfg_rj.removeGuild(ctx.guild.id)
        await ctx.send(
            embed=disnake.Embed(description=f'{emoji.CROSS} РЕЖОКТИРОВАНИЕ ДЕАКТИВИРОВАНО', color=cfg.MAIN_COLOR)
        )
    @commands.is_owner()
    @commands.command('анекдоты')
    async def anecdot_channel(self, ctx: commands.Context):
        if ctx.channel.id not in cfg_rj.getAnekdotChannels():
            cfg_rj.addAnekdotChannel(ctx.channel.id)
            return await ctx.send(
                embed=disnake.Embed(description=f'{emoji.CHECKMARK} Теперь в этом канале будут ежедневные анекдоты', color=cfg.MAIN_COLOR)
            )

        cfg_rj.removeAnekdotChannel(ctx.channel.id)
        await ctx.send(
            embed=disnake.Embed(description=f'{emoji.CROSS} Ежедневные анекдоты отключены в этом канале', color=cfg.MAIN_COLOR)
        )
    @commands.command('даун')
    async def translate_layout(self, ctx: commands.Context, *, text: str = None):
        def fix_layout(source_text: str) -> str:
            eng_chars = "qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?`~@#$^&"
            rus_chars = "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,ёЁ\"№;:?"
            
            trans_table = str.maketrans(eng_chars, rus_chars)
            return source_text.translate(trans_table)
            
        if not text:
            if not ctx.message.reference:
                return await ctx.reply('Ты даун. Ответь на сообщение или добавь текст. Мне чо переводить?')
            original = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            text = original.content
            await original.reply(fix_layout(text))
        else:
            await ctx.reply(fix_layout(text))
    
def setup(bot):
    bot.add_cog(RejactirovanieCog(bot))
