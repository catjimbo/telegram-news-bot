import aiosqlite

DB_PATH = "data/bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                tags TEXT
            )
        """)
        await db.commit()

async def set_user_tags(user_id: int, tags: list[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "REPLACE INTO users (user_id, tags) VALUES (?, ?)",
            (user_id, ','.join(tags))
        )
        await db.commit()

async def get_user_tags(user_id: int) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT tags FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0].split(',')
            return []
