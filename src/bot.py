# Poetry 依賴管理提示：
# 1. 安裝套件：poetry add discord.py python-dotenv plyer
# 2. 運行機器人：poetry run python src/bot.py
# 3. 更新套件：poetry update

import discord
from discord.ext import commands
import json
import os
import asyncio
import logging
import sys
import io

# 在文件開頭添加
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ],
    encoding='utf-8'
)
logger = logging.getLogger('bot')

# 讀取配置
try:
    with open('assets/config.json') as f:
        config = json.load(f)
    logger.info(f"成功載入配置文件")
except Exception as e:
    logger.error(f"載入配置文件失敗：{e}")
    raise

# 創建機器人實例
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # 添加成員權限
bot = commands.Bot(command_prefix=config['PREFIX'], intents=intents)

async def load_extensions():
    """載入所有擴展"""
    try:
        extensions = [
            'commands.start',
            'commands.ping',
            'commands.list',
            'commands.help',  # 新增的 help 指令
        ]
        for extension in extensions:
            try:
                await bot.load_extension(extension)
                logger.info(f"已載入擴展：{extension}")
            except Exception as e:
                logger.error(f"載入擴展 {extension} 失敗：{e}")
                raise
    except Exception as e:
        logger.error(f"載入擴展過程中發生錯誤：{e}")
        raise

@bot.event
async def on_ready():
    logger.info(f'Bot已登入為 {bot.user}')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'目前已載入的指令：{[command.name for command in bot.commands]}')
    logger.info('-------------------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ 您沒有執行此指令的權限！需要 'canOpenServer' 角色。")
    else:
        logger.error(f"指令錯誤：{str(error)}")
        await ctx.send(f"⚠️ 執行指令時發生錯誤：{str(error)}")

async def main():
    try:
        async with bot:
            await load_extensions()
            await bot.start(config['TOKEN'])
    except Exception as e:
        logger.error(f"運行時發生錯誤：{e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被手動中止")
    except Exception as e:
        logger.error(f"程序發生致命錯誤：{e}")
