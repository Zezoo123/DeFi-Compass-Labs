from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from sqlalchemy.sql import text

# Database credentials and connection string
username = "i-can-only-read-gmx-data"
password = "house-football-checksum-11"
host = "34.77.163.253"
port = "5432"
db_name = "dojo_data"

# Create the database URL
db_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"

async def main():
    # Create the async engine
    async_engine = create_async_engine(db_url)

    async with async_engine.connect() as connection:
        # Run the query
        result = await connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        print("Tables in the database:", tables)

    # Dispose of the engine after usage
    await async_engine.dispose()

# Run the async function
asyncio.run(main())