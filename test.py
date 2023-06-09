import asyncio
import time

async def main():
    asyncio.create_task(data())
    print('Hullo')
    time.sleep(2)
    print('Goobye')

async def data():
    print('Data')

asyncio.run(main())