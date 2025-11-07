from disnake.ext import commands
from modules.discordFunctions import removeUserRoles
from modules.database import colorTable
import disnake

class ClearOnLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    # Удаляет цвет при выходе участника с сервера
    @commands.Cog.listener('on_member_remove')
    async def removeColor(self, member: disnake.Member):
        await removeUserRoles(member.guild, member.id)

    # Удаляет цвета участников, вышедших когда бот был в офлайне
    @commands.Cog.listener('on_ready')
    async def clearLeavedAtOffline(self):
        """Очистка данных участников, которые покинули сервер"""
        for guild in self.bot.guilds:
            user_ids = await colorTable.getAllMembersWithColor(guild.id)
            for id in user_ids:
                member = guild.get_member(id)
                if member is None:
                    await removeUserRoles(guild, id)
    
def setup(bot):
    bot.add_cog(ClearOnLeaveCog(bot))
