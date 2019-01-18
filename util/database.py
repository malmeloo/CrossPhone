import asyncio

import aiomysql


class DatabaseConnection:
    """
    A database class to perform commonly used database operations.
    """
    def __init__(self, **kwargs):
        self.loop = asyncio.get_event_loop()

        self.conn = self.loop.run_until_complete(self.connect(**kwargs))

    async def connect(self, **kwargs):
        """
        Connects to the database.
        """
        return await aiomysql.connect(cursorclass=aiomysql.cursors.DictCursor, **kwargs)

    async def get_number(self, number):
        """Returns a specific number from the database."""
        async with self.conn.cursor() as cur:
            stmt = 'SELECT * FROM phone_numbers WHERE number=%s;'
            await cur.execute(stmt, number)
            number_info = await cur.fetchone()

        return number_info

    async def get_all_numbers(self, row='*', limit=100):
        """Returns all numbers in the database."""

        async with self.conn.cursor() as cur:
            stmt = f'SELECT {row} FROM phone_numbers LIMIT %s;'
            await cur.execute(stmt, limit)
            numbers = await cur.fetchall()

        return numbers

    async def add_number(self, number, bot_id, description,
                         channel_id, server_id):
        async with self.conn.cursor() as cur:
            stmt = """INSERT INTO phone_numbers
                   (number, botid, description, channelid, serverid)
                   VALUES (%s, %s, %s, %s, %s);
                   """
            await cur.execute(stmt, (number, bot_id, description,
                                     channel_id, server_id))
        await self.conn.commit()
