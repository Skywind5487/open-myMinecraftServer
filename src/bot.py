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
from pathlib import Path
from src.utils import load_config, get_nested_value

# 在文件開頭添加
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

# 先載入設定檔
config = load_config()

# 創建機器人實例
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix=config['bot']['prefix'],
    intents=intents
)

# 添加設定到 bot 實例
bot.config = config

async def load_extensions():
    """自動載入 commands 目錄下所有合法模組"""
    # 設定指令目錄路徑
    commands_dir = Path("src/commands")
    
    try:
        # 動態掃描所有 .py 檔案
        extensions = [
            f"src.commands.{file.stem}"
            for file in commands_dir.glob("*.py")
            if file.is_file() and not file.name.startswith("_")
        ]

        logger.info(f"找到可載入模組：{extensions}")

        for extension in extensions:
            try:
                await bot.load_extension(extension)
                logger.info(f"✅ 成功載入：{extension}")
            except commands.ExtensionError as e:
                logger.error(f"❌ 載入失敗 {extension}: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"⚠️ 未知錯誤 {extension}: {e}", exc_info=True)

    except Exception as e:
        logger.critical(f"‼️ 目錄掃描失敗：{e}")
        raise

@bot.event
async def on_ready():
    logger.info(f'Bot已登入為 {bot.user}')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'目前已載入的指令：{[command.name for command in bot.commands]}')
    logger.info('-------------------')

    # 在最後加入狀態設定
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="查看Wiki取得幫助",
            state=f"🌐 {config['wiki']['base_url']}",
            details="輸入 !help 取得指令列表"
        ),
        status=discord.Status.online
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ 您沒有執行此指令的權限！需要 'canOpenServer' 角色。")
    else:
        logger.error(f"指令錯誤：{str(error)}")
        await ctx.send(f"⚠️ 執行指令時發生錯誤：{str(error)}")

async def main():
    try:
        # 從 config 取得 token
        token = config["bot"]["token"]
        
        # 檢查關鍵 token
        if not token:
            raise ValueError("DISCORD_TOKEN 未設定！請檢查設定檔或環境變數")
            
        # 添加初始化檢查
        logger.info("=== 系統啟動初始化檢查 ===")
        logger.info(f"Python 版本：{sys.version}")
        logger.info(f"工作目錄：{os.getcwd()}")
        logger.info(f"載入設定：{json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 檢查必要目錄
        required_dirs = ['assets/command_help', 'assets/wiki']
        for d in required_dirs:
            path = Path(d)
            if not path.exists():
                logger.warning(f"建立缺失目錄：{d}")
                path.mkdir(parents=True, exist_ok=True)
        
        # 檢查必要設定
        required_settings = [
            ('wiki.base_url', 'WIKI_URL'),
            ('bot.token', 'DISCORD_TOKEN'),
            ('network.ddns', 'DDNS_HOST')
        ]
        
        for path, env_var in required_settings:
            if not get_nested_value(config, path) and not os.getenv(env_var):
                raise ValueError(f"缺少必要設定：{path} 或環境變數 {env_var}")
        
        # 啟動機器人
        async with bot:
            await load_extensions()
            logger.info("開始連接 Discord 伺服器...")
            logger.info(f"使用的 Token 前 5 字元：{token[:5]}...")
            await bot.start(token)
    except Exception as e:
        logger.critical(f"啟動失敗：{str(e)}", exc_info=True)
        raise
