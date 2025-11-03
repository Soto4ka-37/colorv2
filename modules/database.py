import aiosqlite
import datetime
from modules.colorFunctions import Color
from modules.config import cfg

class Database:
    def __init__(self, path: str):
        self.path = path
        self.db_write: aiosqlite.Connection | None = None
        self.db_read: aiosqlite.Connection | None = None
        self.activated = False

    async def init(self):
        """Инициализация базы данных и включение WAL режима."""
        # Соединение для записи
        self.db_write = await aiosqlite.connect(self.path)
        await self.db_write.execute("PRAGMA journal_mode=WAL;")
        await self.db_write.execute("PRAGMA foreign_keys=ON;")

        # Соединение для чтения
        self.db_read = await aiosqlite.connect(self.path)
        await self.db_read.execute("PRAGMA foreign_keys=ON;")

        if not self.activated:
            await self.create_tables()
            self.activated = True

    async def close(self):
        """Закрытие соединений."""
        if self.db_write:
            await self.db_write.close()
            self.db_write = None
        if self.db_read:
            await self.db_read.close()
            self.db_read = None

    async def create_tables(self):
        """Создание таблиц и индексов."""
        assert self.db_write is not None
        await self.db_write.execute("""
            CREATE TABLE IF NOT EXISTS colors (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                color TEXT NOT NULL,
                timestamp TEXT,
                PRIMARY KEY (guild_id, user_id, role_id)
            );
        """)
        await self.db_write.execute("""
            CREATE TABLE IF NOT EXISTS guild_color_change_roles (
                guild_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, role_id)
            );
        """)
        await self.db_write.execute(
            "CREATE INDEX IF NOT EXISTS idx_guild_role ON colors(guild_id, role_id);"
        )
        await self.db_write.execute(
            "CREATE INDEX IF NOT EXISTS idx_guild ON colors(guild_id);"
        )
        await self.db_write.commit()

    # ------------------------
    # Методы для записи
    # ------------------------
    async def execute_write(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Выполнить INSERT/UPDATE/DELETE с локальным коммитом."""
        assert self.db_write is not None
        cursor = await self.db_write.execute(query, params)
        await self.db_write.commit()
        return cursor

    # ------------------------
    # Методы для чтения
    # ------------------------
    async def fetchall_read(self, query: str, params: tuple = ()) -> list[tuple]:
        """Выполнить SELECT и вернуть все строки."""
        assert self.db_read is not None
        cursor = await self.db_read.execute(query, params)
        return await cursor.fetchall()

    async def fetchone_read(self, query: str, params: tuple = ()) -> tuple | None:
        """Выполнить SELECT и вернуть одну строку."""
        assert self.db_read is not None
        cursor = await self.db_read.execute(query, params)
        return await cursor.fetchone()


# ------------------------
# Таблица цветов
# ------------------------
class DataColor:
    def __init__(self, role_id: int, hex_color: str):
        self.role_id = role_id
        self.color = Color(hex_color)

class ColorTableManager:
    def __init__(self, db: Database):
        self.db = db

    # ------------------------
    # Запись
    # ------------------------
    async def addRole(self, guild_id: int, user_id: int, role_id: int, color: Color):
        await self.db.execute_write("""
            INSERT INTO colors (guild_id, user_id, role_id, color, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id, role_id)
            DO UPDATE SET color=excluded.color;
        """, (guild_id, user_id, role_id, color.hex, datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))

    async def removeUser(self, guild_id: int, user_id: int):
        await self.db.execute_write(
            "DELETE FROM colors WHERE guild_id = ? AND user_id = ?;",
            (guild_id, user_id)
        )

    async def removeRole(self, guild_id: int, role_id: int):
        await self.db.execute_write(
            "DELETE FROM colors WHERE guild_id = ? AND role_id = ?;",
            (guild_id, role_id)
        )

    async def removeGuild(self, guild_id: int):
        await self.db.execute_write(
            "DELETE FROM colors WHERE guild_id = ?;",
            (guild_id,)
        )
        
    async def removeAllInGuild(self, guild_id: int):
        await self.db.execute_write(
            "DELETE FROM colors WHERE guild_id = ?;",
            (guild_id,)
        )

    # ------------------------
    # Чтение
    # ------------------------
    async def getAllMembersWithColor(self, guild_id: int) -> tuple[int]:
        rows = await self.db.fetchall_read(
            "SELECT user_id FROM colors WHERE guild_id = ?;",
            (guild_id,)
        )
        return tuple(row[0] for row in rows)
    
    async def getAllByUser(self, guild_id: int, user_id: int) -> tuple[DataColor, ...]:
        rows = await self.db.fetchall_read(
            "SELECT role_id, color FROM colors WHERE guild_id = ? AND user_id = ?;",
            (guild_id, user_id)
        )
        return tuple(DataColor(*row) for row in rows)

    async def getLastByUser(self, guild_id: int, user_id: int) -> DataColor | None:
        row = await self.db.fetchone_read(
            """
            SELECT role_id, color 
            FROM colors 
            WHERE guild_id = ? AND user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1;
            """,
            (guild_id, user_id)
        )
        if row is None:
            return None
        return DataColor(*row)

    
    async def getByUser(self, guild_id: int, user_id: int, role_id: int) -> DataColor | None:
        row = await self.db.fetchone_read(
            "SELECT color FROM colors WHERE guild_id = ? AND user_id = ? AND role_id = ?;",
            (guild_id, user_id, role_id)
        )
        if row is None:
            return None
        return DataColor(role_id, row[0])


class GuildColorChangeRolesTableManager:
    def __init__(self, db: Database):
        self.db = db

    # ------------------------
    # Запись
    # ------------------------
    async def addRole(self, guild_id: int, role_id: int):
        await self.db.execute_write("""
            INSERT INTO guild_color_change_roles (guild_id, role_id)
            VALUES (?, ?)
        """, (guild_id, role_id))

    async def removeRole(self, guild_id: int, role_id: int):
        await self.db.execute_write(
            "DELETE FROM guild_color_change_roles WHERE guild_id = ? AND role_id = ?;",
            (guild_id, role_id)
        )

    async def removeGuild(self, guild_id: int):
        await self.db.execute_write(
            "DELETE FROM guild_color_change_roles WHERE guild_id = ?;",
            (guild_id,)
        )
        
    # ------------------------
    # Чтение
    # ------------------------
    async def getAllByGuild(self, guild_id: int) -> tuple[int, ...]:
        rows = await self.db.fetchall_read(
            "SELECT role_id FROM guild_color_change_roles WHERE guild_id = ?;",
            (guild_id,)
        )
        return tuple(row[0] for row in rows)

    async def roleInGuild(self, guild_id: int, role_id: int):
        row = await self.db.fetchone_read(
            "SELECT 1 FROM guild_color_change_roles WHERE guild_id = ? AND role_id = ? LIMIT 1;",
            (guild_id, role_id)
        )
        return row is not None
        
# ------------------------
# Инициализация
# ------------------------
db = Database(cfg.DB_PATH)
colorTable = ColorTableManager(db)
guildChangeRolesTable = GuildColorChangeRolesTableManager(db)
async def initDatabase():
    await db.init()