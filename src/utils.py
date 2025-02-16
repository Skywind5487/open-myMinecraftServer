import os
import json
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_nested_value(data, keys):
    """安全獲取嵌套字典值"""
    current = data
    for key in keys.split('.'):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def load_config():
    """載入設定檔，優先使用環境變數"""
    load_dotenv()
    file_config = {}
    config_path = Path("assets/config.json")
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
        except Exception as e:
            logger.error(f"載入設定檔失敗: {e}")
    
    return {
        "bot": {
            "prefix": os.getenv("BOT_PREFIX", file_config.get("bot", {}).get("prefix", "!")),
            "token": os.getenv("DISCORD_TOKEN", file_config.get("bot", {}).get("token", "")),
            "status": os.getenv("BOT_STATUS", file_config.get("bot", {}).get("status", "Minecraft 伺服器管理"))
        },
        "wiki": {
            "base_url": os.getenv("WIKI_BASE_URL", 
                                file_config.get("wiki", {}).get(
                                    "base_url", 
                                    "https://raw.githubusercontent.com/Skywind5487/open-myMinecraftServer/main/assets/wiki"
                                )),
            "default_page": os.getenv("WIKI_DEFAULT_PAGE", 
                                    file_config.get("wiki", {}).get("default_page", "index.md"))
        },
        "network": {
            "ddns": os.getenv("DDNS_HOST", file_config.get("network", {}).get("ddns", "localhost")),
            "alist": {
                "url": os.getenv("ALIST_URL", 
                               file_config.get("network", {}).get("alist", {}).get("url", "")),
                "http_port": int(os.getenv("ALIST_HTTP_PORT", 
                                         file_config.get("network", {}).get("alist", {}).get("http_port", 5244))),
                "https_port": int(os.getenv("ALIST_HTTPS_PORT", 
                                          file_config.get("network", {}).get("alist", {}).get("https_port", 5245))),
                "username": os.getenv("ALIST_USERNAME", 
                                    file_config.get("network", {}).get("alist", {}).get("username", "")),
                "password": os.getenv("ALIST_PASSWORD", 
                                    file_config.get("network", {}).get("alist", {}).get("password", ""))
            }
        },
        "server": {
            "base_path": os.getenv("SERVER_BASE_PATH", 
                                 file_config.get("server", {}).get("base_path", ""))
        },
        "command_colors": file_config.get("command_colors", {})
    }

    # 添加設定結構驗證
    try:
        return {
            "bot": {
                "prefix": os.getenv("BOT_PREFIX", file_config.get("bot", {}).get("prefix", "!")),
                "status": os.getenv("BOT_STATUS", file_config.get("bot", {}).get("status", "Minecraft 伺服器管理"))
            },
            "wiki": {
                "base_url": os.getenv("WIKI_BASE_URL", 
                                    file_config.get("wiki", {}).get(
                                        "base_url", 
                                        "https://raw.githubusercontent.com/Skywind5487/open-myMinecraftServer/main/assets/wiki"
                                    )),
                "default_page": os.getenv("WIKI_DEFAULT_PAGE", 
                                        file_config.get("wiki", {}).get("default_page", "index.md"))
            },
            "network": {
                "ddns": os.getenv("DDNS_HOST", file_config.get("network", {}).get("ddns", "localhost")),
                "alist": {
                    "http": int(os.getenv("ALIST_HTTP_PORT", file_config.get("network", {}).get("alist", {}).get("http", 5244))),
                    "https": int(os.getenv("ALIST_HTTPS_PORT", file_config.get("network", {}).get("alist", {}).get("https", 5245)))
                }
            },
            "command_colors": file_config.get("command_colors", {})
        }
    except KeyError as e:
        logger.error(f"設定檔結構錯誤，缺少必要鍵: {e}")
        return {
            "bot": {"prefix": "!", "status": "Minecraft 伺服器管理"},
            "wiki": {"base_url": "https://example.com/wiki", "default_page": "index.md"},
            "network": {"ddns": "localhost", "alist": {"http": 5244, "https": 5245}},
            "command_colors": {}
        } 