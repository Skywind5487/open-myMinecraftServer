import pytest
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_help_command():
    """測試 help 指令"""
    from src.commands.help import CustomHelp
    
    bot = create_test_bot()
    ctx = MockContext()
    
    # 測試正常情況
    cog = CustomHelp(bot)
    await cog.help(ctx, command_name="ping")
    assert ctx.sent_embed is not None
    
    # 測試錯誤情況
    await cog.help(ctx, command_name="invalid_command")
    assert "找不到此指令說明" in ctx.sent_content 