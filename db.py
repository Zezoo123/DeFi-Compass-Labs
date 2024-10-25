from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from sqlalchemy.sql import text
import pandas as pd
from utils import calculate_price

# Database credentials and connection string
username = "i-can-only-read-gmx-data"
password = "house-football-checksum-11"
host = "34.77.163.253"
port = "5432"
db_name = "dojo_data"

# Create the database URL
db_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"
swap_analysis = []
async def main():
    # Create the async engine
    async_engine = create_async_engine(db_url)

    async with async_engine.connect() as connection:
        # Run the query
        result = await connection.execute(text("SELECT block_timestamp, event_name, event_data, transaction_hash, gas_price FROM hackathon_ethereum_events WHERE event_name = 'Swap' ORDER BY block_timestamp DESC OFFSET 0 ROWS FETCH FIRST 5 ROWS ONLY;"))
        sql_result = result.fetchall()
        df = pd.DataFrame(sql_result)
        event_data = df['event_data']
        for row in sql_result:
            timestamp, event_name, event_data, tx_hash, gas_price = row
            sqrt_price_x96 = event_data['sqrtPriceX96']
            price = calculate_price(sqrt_price_x96) #NOT SURE ABOUT PRICE CALCULATION

            swap_analysis.append({
                "timestamp": timestamp,
                "event_name": event_name,
                "sender": event_data['sender'],
                "recipient": event_data['recipient'],
                "amount0": event_data['amount0'],
                "amount1": event_data['amount1'],
                "price": price,
                "transaction_hash": tx_hash,
                "gas_price": gas_price
            })
            
    # Dispose of the engine after usage
    await async_engine.dispose()

# Run the async function

asyncio.run(main())

df_swaps = pd.DataFrame(swap_analysis)

print(df_swaps)