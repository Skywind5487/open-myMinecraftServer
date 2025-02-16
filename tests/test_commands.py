import discord
import discord.ext.commands as commands
import asyncio
from src.utils import load_config
import pytest
from unittest.mock import AsyncMock

class MockContext:
    """模擬 Discord 指令上下文"""
    def __init__(self):
        self.sent_content = None
        self.sent_embed = None
        
    async def send(self, content=None, embed=None):
        self.sent_content = content
        self.sent_embed = embed
        return None

@pytest.fixture(scope="session")
def event_loop():
    """提供事件循環"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def create_test_bot():
    """建立測試用機器人實例"""
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.config = {
        "bot": {
            "prefix": "!",
            "token": "test_token",
            "status": "測試狀態"
        },
        "wiki": {
            "base_url": "https://test.wiki",
            "default_page": "test.md"
        },
        "network": {
            "ddns": "test.ddns.com",
            "alist": {
                "url": "http://localhost",
                "http_port": 5244,
                "https_port": 5245,
                "username": "test",
                "password": "test"
            }
        },
        "server": {
            "base_path": "/test/path"
        },
        "command_colors": {
            "ping": 0x00ff00
        }
    }
    return bot

@pytest.mark.asyncio
async def test_ping_command():
    """測試 ping 指令"""
    from src.commands.ping import Ping
    
    bot = create_test_bot()
    ctx = MockContext()
    cog = Ping(bot)
    await cog.ping(ctx)
    assert "ms" in ctx.sent_content, f"實際回應內容：{ctx.sent_content}"

@pytest.mark.asyncio
async def test_alist_command():
    """測試 alist 指令"""
    from src.commands.alist import AListCommands
    
    bot = create_test_bot()
    ctx = MockContext()
    
    cog = AListCommands(bot)
    
    await cog.alist(ctx)
    
    assert "Alist 雲端儲存資訊" in ctx.sent_content
    assert "服務器: http://localhost:5244" in ctx.sent_content
    assert "帳號: test" in ctx.sent_content 