import discord
from discord.ext import commands
import logging
from src.services.server import MinecraftServer
from src.cogs.minecraft import MinecraftCommands

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinecraftBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        logger.info("初始化 MinecraftBot")

    async def setup_hook(self):
        logger.info("機器人初始化完成")

async def run_bot(token: str):
    bot = MinecraftBot()
    server = MinecraftServer("D:/2_repo/Game/MC/sever/open-myMinecraftServer/minecraft")
    
    # 載入 Cog
    await bot.add_cog(MinecraftCommands(bot, server))
    logger.info("已載入所有 Cogs")

    @bot.event
    async def on_ready():
        logger.info(f'Bot 已登入為 {bot.user}')
        logger.info("可用指令:")
        for command in bot.commands:
            logger.info(f"  - {bot.command_prefix}{command.name}: {command.help}")

    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Bot 啟動失敗: {e}")
