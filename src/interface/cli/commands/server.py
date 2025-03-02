from pathlib import Path
from typing import Dict, List
import json
from src.service.server_service import add_server, remove_server, list_servers
from src.service.server_service import start_server, stop_server

CONFIG_PATH = Path("config/server.json")

def setup():
    all_commands = []
    all_commands.append(handle_list)
    all_commands.append(handle_add_server)
    all_commands.append(handle_remove_server)
    all_commands.append(handle_start_server)
    all_commands.append(handle_stop_server)

    return all_commands


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

async def handle_start_server(server_identifier: str) -> bool:
    if not server_identifier:
        print("需要提供伺服器 ID")
        print("語法: start <名稱_版本號>")
        return True

    try:
        started_server = await start_server(server_identifier)
        print(f"已啟動伺服器：{started_server['name']} ({started_server['version']})")
        return True
    except Exception as e:
        print(f"錯誤：{e}")
        return True

async def handle_stop_server(server_identifier: str) -> bool:
    if not server_identifier:
        print("需要提供伺服器 ID")
        print("語法: stop <名稱_版本號>")
        return True

    try:
        stopped_server = await stop_server(server_identifier)
        print(f"已停止伺服器：{stopped_server['name']} ({stopped_server['version']})")
        return True
    except Exception as e:
        print(f"錯誤：{e}")
        return True