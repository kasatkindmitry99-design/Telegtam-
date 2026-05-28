from datetime import datetime
import aiosqlite


async def get_users():

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            "SELECT * FROM users"
        ) as cursor:

            return await cursor.fetchall()

async def get_all_telegram_ids():

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            "SELECT telegram_id FROM users"
        ) as cursor:

            return await cursor.fetchall()

async def user_exists(telegram_id):

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            """
            SELECT id FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,)
        ) as cursor:

            user = await cursor.fetchone()

            return user is not None

async def add_user(telegram_id, name, phone):

    created_at = datetime.now().strftime(
    "%d.%m.%Y %H:%M"
    )

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        await db.execute(
            """
            INSERT INTO users
            (
                telegram_id,
                name,
                phone,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                telegram_id,
                name,
                phone,
                created_at
            )
        )

        await db.commit()


async def delete_user(user_id):

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        await db.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        await db.commit()

async def search_users(search):

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            """
            SELECT * FROM users
            WHERE name LIKE ?
            OR phone LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        ) as cursor:

            return await cursor.fetchall()

async def get_stats():

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            "SELECT COUNT(*) FROM users"
        ) as cursor:

            total = (await cursor.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE status = 'new'"
        ) as cursor:

            new = (await cursor.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE status = 'work'"
        ) as cursor:

            work = (await cursor.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE status = 'closed'"
        ) as cursor:

            closed = (await cursor.fetchone())[0]

        return {

            "total": total,

            "new": new,

            "work": work,

            "closed": closed
        }

async def get_users_by_status(status):

    async with aiosqlite.connect(
        "database.db"
    ) as db:

        async with db.execute(
            "SELECT * FROM users WHERE status = ?",
            (status,)
        ) as cursor:

            return await cursor.fetchall()