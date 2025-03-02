from pathlib import Path
from typing import Dict, List
import json
from src.service.server_service import add_server, remove_server, list_servers

CONFIG_PATH = Path("config/server.json")

async def handle_list() -> bool:
    try:
        servers = await list_servers()
        if not servers:
            print("尚無伺服器")
            return True
            
        print("\n=== 伺服器列表 ===")
        for server in servers:
            status = "🟢 在線" if server["status"] == "online" else "🔴 離線"
            print(f"{status} - {server['name']} ({server['version']})")
        return True
    except Exception as e:
        print(f"錯誤：{e}")
        return True

async def handle_add_server(path: str, force: bool = False, desc: str = "") -> bool:
    try:
        if not path:
            print("需要提供伺服器路徑")
            return True
            
        server = await add_server(path, force, desc)
        print(f"已新增伺服器：{server['name']}")
        return True
    except Exception as e:
        print(f"錯誤：{e}")
        return True

async def handle_remove_server(server_id: str) -> bool:
    if not server_id:
        print("需要提供伺服器 ID")
        return True
        
    try:
        removed_server = await remove_server(server_id)
        print(f"已移除伺服器：{removed_server['name']} ({removed_server['version']})")
        return True
    except Exception as e:
        print(f"錯誤：{e}")
        return True
