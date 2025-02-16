from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_alist_command_success():
    """測試 alist 指令成功情況"""
    from src.commands.alist import AListCommands
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"data": [...]}
    
    bot = create_test_bot()
    bot.config["network"]["alist"] = {
        "url": "http://test",
        "token": "test_token"
    }
    cog = AListCommands(bot)
    cog.http_client = AsyncMock()
    cog.http_client.get.return_value = mock_response
    
    ctx = MockContext()
    await cog.alist(ctx)
    
    assert "雲端管理資訊" in ctx.sent_embed.title 