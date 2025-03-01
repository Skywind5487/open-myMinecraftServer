import asyncio
from src.main import run_bot
from dotenv import load_dotenv
import os

async def main():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("錯誤：找不到 DISCORD_TOKEN 環境變數")
        return
    await run_bot(token)

if __name__ == "__main__":
    asyncio.run(main())
