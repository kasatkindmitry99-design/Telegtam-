import aiosqlite

async def create_db():

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT
            )
            """
        )

        await db.commit()