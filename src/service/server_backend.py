import asyncio
import json
import os
from pathlib import Path
async def add_server(server_path: str):
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"伺服器路徑不存在: {server_path}")
    
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'server.json'

    # 統一使用 server_paths 作為鍵名
    if not config_file.exists():    
        servers = {
            "server_paths": []  # 改正鍵名
        }
    else:
        with open(config_file, 'r', encoding='utf-8') as f:
            try:
                servers = json.load(f)
                # 確保有正確的鍵名
                if "server_paths" not in servers:
                    servers["server_paths"] = []
            except json.JSONDecodeError:
                servers = {
                    "server_paths": []  # 改正鍵名
                }

    normalized_path = os.path.normpath(server_path)
    if normalized_path in servers["server_paths"]:  # 改正鍵名
        raise ValueError(f"伺服器路徑已存在: {normalized_path}")
    
    servers["server_paths"].append(normalized_path)  # 保持一致的鍵名
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(servers, f, ensure_ascii=False, indent=2)