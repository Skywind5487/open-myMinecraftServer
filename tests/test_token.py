import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
import pytest

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN").strip()

class TokenTestBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default()
        )
    
    async def on_ready(self):
        print(f"成功登入為 {self.user}!")
        await self.close()

@pytest.mark.asyncio
async def test_token_validity():
    """測試 Discord Token 有效性"""
    bot = TokenTestBot()
    await bot.start(TOKEN) 