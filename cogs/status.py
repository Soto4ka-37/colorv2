from disnake.ext import commands
import disnake

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        activity = disnake.Activity(
            type=disnake.ActivityType.custom,
            state="Меняет !цвет • v2.1.0",
            name='-', # Заглушка, так как имя берётся из state
        )
        await self.bot.change_presence(status=disnake.Status.idle, activity=activity)
        
def setup(bot):
    bot.add_cog(Status(bot))