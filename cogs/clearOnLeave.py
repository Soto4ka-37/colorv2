from disnake.ext import commands
from modules.discordFunctions import removeUserRoles
import disnake

class ClearOnLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener('on_member_remove')
    async def removeColor(member: disnake.Member):
        await removeUserRoles(member.guild, member.id)

def setup(bot):
    bot.add_cog(ClearOnLeaveCog(bot))
