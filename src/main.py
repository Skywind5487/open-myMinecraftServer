import os
from dotenv import load_dotenv
from discord.ext import commands
import json

# 載入環境變數
load_dotenv()

# 預設設定值
DEFAULT_CONFIG = {
    "bot": {
        "prefix": "!",
        "status": "Minecraft 伺服器管理"
    },
    "wiki": {
        "base_url": "https://skywind1234.asuscomm.com/wiki"
    },
    "network": {
        "ddns": "skywind1234.asuscomm.com",
        "alist": {
            "http": 5244,
            "https": 5245
        }
    }
}

def load_config():
    """載入設定檔，優先使用環境變數"""
    try:
        with open('assets/config.json') as f:
            file_config = json.load(f)
    except FileNotFoundError:
        file_config = {}

    return {
        "bot": {
            "prefix": os.getenv("BOT_PREFIX", file_config.get("bot_settings", {}).get("prefix", DEFAULT_CONFIG["bot"]["prefix"])),
            "status": os.getenv("BOT_STATUS", file_config.get("bot_settings", {}).get("status", DEFAULT_CONFIG["bot"]["status"]))
        },
        "wiki": {
            "base_url": os.getenv("WIKI_BASE_URL", file_config.get("wiki_settings", {}).get("base_url", DEFAULT_CONFIG["wiki"]["base_url"]))
        },
        "network": {
            "ddns": os.getenv("DDNS_HOST", 
                file_config.get("DDNS", DEFAULT_CONFIG["network"]["ddns"])),
            "alist": {
                "http": int(os.getenv("ALIST_HTTP_PORT", 
                    file_config.get("ALIST", {}).get("http_port", 5244))),
                "https": int(os.getenv("ALIST_HTTPS_PORT", 
                    file_config.get("ALIST", {}).get("https_port", 5245)))
            }
        }
    }

config = load_config()

bot = commands.Bot(
    command_prefix=config['bot_settings']['prefix'],
    intents=intents
)

# 原本的啟動方式
# bot.run(config['bot_settings']['token'])

# 改為從環境變數讀取
bot.run(os.getenv("DISCORD_TOKEN")) 