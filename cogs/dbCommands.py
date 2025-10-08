import disnake
from disnake.ext import commands
from modules.database import db
import traceback

class DbCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.is_owner()
    @commands.slash_command(name='db')
    async def db_cmd(self, inter: disnake.ApplicationCommandInteraction):
        pass
    
    @db_cmd.sub_command(name='execute', description='Выполнить INSERT/UPDATE/DELETE с локальным коммитом.')
    async def execute(self, inter: disnake.ApplicationCommandInteraction, query: str):
        try:
            await db.execute_write(query)
            await inter.send(embed=disnake.Embed(title='Успех', description='Действие выполнено'))
        except Exception as e:
            await inter.send(ephemeral=True, embed=disnake.Embed(title=f'Исключение {type(e).__name__}', description=f'```py\n{traceback.format_exc()}```'))

    @db_cmd.sub_command(name='fetchall', description='Выполнить SELECT и вернуть все строки.')
    async def fetch_all(self, inter: disnake.ApplicationCommandInteraction, query: str):
        try:
            results = await db.fetchall_read(query)
            await inter.send(embed=disnake.Embed(title='Результаты', description=f'```py\n{results}```'))
        except Exception as e:
            await inter.send(ephemeral=True, embed=disnake.Embed(title=f'Исключение {type(e).__name__}', description=f'```py\n{traceback.format_exc()}```'))

    @db_cmd.sub_command(name='fetchone', description='Выполнить SELECT и вернуть одну строку.')
    async def fetch_one(self, inter: disnake.ApplicationCommandInteraction, query: str):
        try:
            result = await db.fetchone_read(query)
            await inter.send(embed=disnake.Embed(title='Результат', description=f'```py\n{result}```'))
        except Exception as e:
            await inter.send(ephemeral=True, embed=disnake.Embed(title=f'Исключение {type(e).__name__}', description=f'```py\n{traceback.format_exc()}```'))

def setup(bot):
    bot.add_cog(DbCog(bot))
