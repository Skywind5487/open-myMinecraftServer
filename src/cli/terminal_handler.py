from src.service.server_backend import add_server, remove_server
import json
import os
from pathlib import Path
import asyncio

async def handle_add_server(args):
    """處理終端機的 add 指令"""
    force = False
    description = ""
    server_path = None
    
    # 解析參數
    i = 0
    while i < len(args):
        if args[i] == '-f':
            force = True
        elif args[i] == '-d':
            i += 1
            if i < len(args):
                description = args[i]
        else:
            server_path = args[i]
        i += 1

    if not server_path:
        print("錯誤：請提供伺服器路徑")
        return False

    try:
        server_info = await add_server(server_path, force=force, description=description)
        print("\n✅ 伺服器新增成功！")
        print(f"名稱: {server_info['name']}")
        print(f"版本: {server_info['version']}")
        print(f"核心: {server_info['core_type']}")
        print(f"端口: {server_info['port']}")
        print(f"路徑: {server_info['path']}")
        if force:
            print("\n注意：使用了強制模式 (-f) 添加")
        return True
    except Exception as e:
        print(f"\n❌ 錯誤：{str(e)}")
        return False

async def handle_remove_server(args):
    """處理終端機的 remove 指令"""
    if not args:
        print("錯誤：請提供要移除的伺服器標識符 (格式: 名稱_版本)")
        return False

    try:
        server = await remove_server(args[0])
        print("\n🗑️ 伺服器移除成功！")
        print(f"名稱: {server['name']}")
        print(f"版本: {server['version']}")
        print(f"核心: {server['core_type']}")
        print(f"端口: {server['port']}")
        print(f"路徑: {server['path']}")
        return True
    except Exception as e:
        print(f"\n❌ 錯誤：{str(e)}")
        return False

async def handle_list():
    """處理終端機的 list 指令"""
    config_path = Path("config/server.json")
    
    if not config_path.exists():
        print("找不到伺服器設定檔！")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        servers = data.get("servers", [])

    if not servers:
        print("目前還沒有新增任何 Minecraft 伺服器！")
        return False

    print("\n=== Minecraft 伺服器清單 ===")
    for server in servers:
        status_icon = "🟢" if server["status"] == "online" else "🔴"
        status_text = "在線" if server["status"] == "online" else "離線"
        print(f"\n{status_icon} {server['name']}")
        print(f"  版本: {server['version']}")
        print(f"  端口: {server['port']}")
        print(f"  核心: {server['core_type']}")
        print(f"  狀態: {status_text}")
    print("\n===========================")
    return True

# 確保函數可以被匯出
__all__ = ['handle_terminal_command']

async def handle_terminal_command(command: str):
    """處理終端機指令"""
    parts = command.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "add_server":
        await handle_add_server(args)
    elif cmd in ["remove_server", "rm_server"]:
        await handle_remove_server(args)
    elif cmd == "list":
        await handle_list()
    elif cmd in ["exit", "quit"]:
        return False
    elif cmd == "help":
        print("\n可用指令：")
        print("  add_server [-f] [-d description] <伺服器路徑> - 新增伺服器")
        print("  remove_server/rm_server <名稱_版本> - 移除伺服器")
        print("  list - 顯示伺服器列表")
        print("  exit/quit - 退出程式")
        print("  help - 顯示此幫助訊息")
    else:
        print(f"未知指令：{cmd}")
    
    return True
