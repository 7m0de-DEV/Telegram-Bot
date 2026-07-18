import os
import aiosqlite



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "bot_stats.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                upload_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                item_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def log_activity(user_id: int, username: str, action: str, item_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, last_active, download_count, upload_count)
            VALUES (?, ?, CURRENT_TIMESTAMP, 0, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                last_active = CURRENT_TIMESTAMP
        """, (user_id, username))

        column = "download_count" if action == "download" else "upload_count"
        await db.execute(f"UPDATE users SET {column} = {column} + 1 WHERE user_id = ?", (user_id,))

        await db.execute(
            "INSERT INTO activity_log (user_id, action, item_name) VALUES (?, ?, ?)",
            (user_id, action, item_name)
        )
        await db.commit()

async def get_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT download_count, upload_count, first_seen FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_global_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*), SUM(download_count), SUM(upload_count) FROM users"
        ) as cursor:
            return await cursor.fetchone()


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]