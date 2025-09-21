from disnake.ext import commands
import psutil

from aiohttp import web

# Переменные
IP_ADDRESS = 'localhost'
PORT = 30002

class API(web.Application):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.site = None
        self.runner = None
        self.router.add_get('/api/latency', self.latency)
        
    async def latency(self, r: web.Request):
        try:
            bot = self.bot
            ping = int(bot.latency * 1000)

            pid = psutil.Process()
            memory_info = pid.memory_info()

            return web.json_response({
                'pid': pid.pid,
                'dbver': 3,
                'dbsize': 0,
                'discord_ping': ping,
                'memory': {'rss': int(memory_info.rss),
                            'vms': int(memory_info.vms)},
            }, status=200)
        
        except Exception as e:
            return web.json_response({'error': f'Произошла ошибка <{str(e)}>'}, status=500)
    
    async def _run(self):
        self.runner = web.AppRunner(self)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, IP_ADDRESS, PORT)
        await self.site.start()

    async def stop(self):
        if self.site:
            await self.site.stop()
            self.site = None
        if self.runner:
            await self.runner.cleanup()
            self.runner = None

    async def run(self):
        await self.stop()
        self.bot.loop.create_task(self._run())

class ApiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(ApiCog(bot))
    bot.loop.create_task(API(bot=bot).run())