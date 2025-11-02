import disnake
from disnake.ext import commands
from modules.ui import UniversalUiMessage, AutoPaginatorView
from modules.database import guildChangeRolesTable
from modules.config import cfg
from modules.emojis import emoji
async def checkMemberAccess(member: disnake.Member):
    role_ids = await guildChangeRolesTable.getAllByGuild(member.guild.id)
    if not role_ids:
        return True  # Доступ с любой ролью

    has_role = False
    for role_id in role_ids:
        role = member.guild.get_role(role_id)
        if role is None:
            await guildChangeRolesTable.removeRole(member.guild.id, role_id)  # Очистка удалённых ролей
            continue
        if role in member.roles:
            has_role = True
    return has_role

class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.slash_command(name=disnake.Localized('settings', key='SETTINGS_NAME'))
    async def settings(self, inter: disnake.ApplicationCommandInteraction):
        pass
    
    @settings.sub_command_group(name=disnake.Localized('access', key='ACCESS_NAME'))
    async def access(self, inter: disnake.ApplicationCommandInteraction):
        pass
    
    @access.sub_command(
        name=disnake.Localized('add', key='ADD_NAME'),
        description='Добавить роль, владельцы которой смогут использовать команду цвет.'
    )
    async def access_add(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role = commands.Param(
            name=disnake.Localized('role', key='ROLE_NAME'),
            description="Владельцы этой роли смогут использовать команду цвет.",
        )):
        ui = UniversalUiMessage()
        await ui.init(inter)
    
        exists = await guildChangeRolesTable.roleInGuild(ui.owner.guild.id, role.id)
        if exists:
            embed = disnake.Embed(
                description=f'{emoji.CROSS} Роль {role.mention} уже добавлена в список разрешённых.',
                color=cfg.ERROR_COLOR
            )
            
            return await ui.edit(embed)
        
        await guildChangeRolesTable.addRole(ui.owner.guild.id, role.id)
        embed = disnake.Embed(
            description=f'{emoji.CHECKMARK} Роль {role.mention} успешно добавлена в список разрешённых.',
            color=cfg.MAIN_COLOR
        )
        
        await ui.edit(embed)
        
    @access.sub_command(
        name=disnake.Localized('remove', key='REMOVE_NAME'),
        description='Убрать роль, владельцы которой смогут использовать команду цвет.'
    )
    async def access_remove(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role = commands.Param(
            name=disnake.Localized('role', key='ROLE_NAME'),
            description="Владельцы этой роли больше не смогут использовать команду цвет.",
        )):
        ui = UniversalUiMessage()
        await ui.init(inter)
        
        exists = await guildChangeRolesTable.roleInGuild(ui.owner.guild.id, role.id)
        if not exists:
            embed = disnake.Embed(
                description=f'{emoji.CROSS} Роль {role.mention} не найдена в списке разрешённых.',
                color=cfg.ERROR_COLOR
            )
            
            return await ui.edit(embed)

        await guildChangeRolesTable.removeRole(ui.owner.guild.id, role.id)
        embed = disnake.Embed(
            description=f'{emoji.CHECKMARK} Роль {role.mention} успешно удалена из списка разрешённых.',
            color=cfg.MAIN_COLOR
        )
        
        await ui.edit(embed)
        
    @access.sub_command(
        name=disnake.Localized('list', key='LIST_NAME'),
        description='Список ролей которые могут использовать цвет.'
    )
    async def access_list(self, inter: disnake.ApplicationCommandInteraction):
        ui = UniversalUiMessage()
        await ui.init(inter)
        
        roles = await guildChangeRolesTable.getAllByGuild(ui.owner.guild.id)
        if not roles:
            embed = disnake.Embed(
                description=f'🎉 У вас нет привязки к ролям!\n{emoji.GEAR} Чтобы включить ограничение, добавьте сюдаы хотя бы одну роль.',
                color=cfg.MAIN_COLOR
            )
            return await ui.edit(embed)
        
        guild_roles = []
        for role_id in roles:
            role = ui.owner.guild.get_role(role_id)
            if role:
                guild_roles.append(role.mention)
            else:
                await guildChangeRolesTable.removeRole(ui.owner.guild.id, role_id)
                
        view = AutoPaginatorView(ui, 'Роли в белом списке', ', '.join(guild_roles))
        await view.show_page()

def setup(bot):
    bot.add_cog(Settings(bot))
