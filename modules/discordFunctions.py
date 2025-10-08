import disnake
from modules.colorFunctions import Color
from modules.database import colorTable
from disnake.ext import commands
async def checkBotPermissions(guild: disnake.Guild):
    '''Проверяет права бота для выполнения действий'''
    bot_member = guild.me
    permissions = []
    if not bot_member.guild_permissions.manage_roles:
        permissions.append("manage_roles")
    
    if len(permissions) > 0:
        raise permissions
    return True

async def generateRole(member: disnake.Member, color: Color) -> disnake.Role:
    '''Создаёт роль согласно заданному цвету и сохраняет в базе данных'''
    try:
        role = await member.guild.create_role(
            name=f'ЦВЕТ-{color.text}',
            color=color.disnakeColor,
            reason=f'Создание персонального цвета для @{member} ({member.id})'
        )
        await colorTable.addRole(member.guild.id, member.id, role.id, color)
        return role
    except disnake.Forbidden:
        raise commands.BotMissingPermissions(['manage_roles'])

    
async def removeRole(guild: disnake.Guild, role_id: int) -> bool:
    '''Удаляет роль из базы данных и сервера возвращает True если успешно'''
    role = guild.get_role(role_id)
    if not role:
        await colorTable.removeRole(guild.id, role_id)
        return True
    try:
        await role.delete(reason='Удаление персональной роли')
        await colorTable.removeRole(guild.id, role_id)
        return True
    except disnake.Forbidden:
        return False

async def removeUserRoles(guild: disnake.Guild, user_id: int) -> list[int]:
    '''Удаляет все роли пользователя с сервера и из базы данных, возвращает список не удалённых ролей'''
    data_colors = await colorTable.getAllByUser(guild.id, user_id)
    not_removed: list[int] = []
    for data_color in data_colors:
        role = guild.get_role(data_color.role_id)
        if role:
            try:
                await role.delete(reason='Удаление персональной роли')
            except disnake.Forbidden:
                not_removed.append(role.id)
    await colorTable.removeUser(guild.id, user_id)
    return not_removed
    
async def moveRole(member: disnake.Member, role: disnake.Role) -> list[str]:
    '''Перемещает роль на уровень пользователя или максимально возможный, возвращает список предупреждений'''
    bot_member = member.guild.me
    warnings: list[str] = []

    if member.top_role.is_default():
        return []

    need_pos = member.top_role.position
    max_pos = bot_member.top_role.position - 1

    if role.position == need_pos or role.position == max_pos:
        return []

    if role.position > max_pos:
        return ["Недостаточно прав. Роль бота ниже роли цвета, бот не может её переместить."]

    if need_pos > max_pos:
        pos = max_pos
        warnings.append(
            f"Недостаточно прав. Роль бота ниже верхней роли пользователя ({member.top_role.mention}), "
            "цвет был установлен на максимально возможный уровень."
        )
    else:
        pos = need_pos

    try:
        await role.edit(position=pos, reason='Перемещение на уровень пользователя или максимально возможный')
    except disnake.Forbidden:
        return ["Недостаточно прав для изменения позиции роли."]

    return warnings

