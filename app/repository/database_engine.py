import asyncpg


class DatabaseEngine:
    def __init__(self, asyncpg_uri: str) -> None:
        self.asyncpg_uri = asyncpg_uri
        self.connection_pool = None

    async def init_connection_pool(self) -> None:
        self.connection_pool = await asyncpg.create_pool(self.asyncpg_uri)

    async def execute(self, statement: str, *args) -> None:
        async with self.connection_pool.acquire() as conn:
            return await conn.execute(statement, *args)

    async def fetch(self, statement: str, *args) -> None:
        async with self.connection_pool.acquire() as conn:
            return await conn.fetch(statement, *args)

    async def executemany(self, statement: str, *args) -> None:
        async with self.connection_pool.acquire() as conn:
            return await conn.executemany(statement, *args)

    async def close(self):
        return await self.connection_pool.terminate()
