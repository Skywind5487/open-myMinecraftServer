import asyncio
import json
import os
import re
from pathlib import Path
import subprocess
import psutil
from datetime import datetime
from plyer import notification
import logging
import time

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

async def add_server(server_path: str, force: bool = False, description: str = "") -> dict:
    """
    添加一個新的 Minecraft 伺服器到配置文件中。
    
    Args:
        server_path (str): 伺服器啟動檔案的完整路徑
        force (bool): 是否略過資料夾名稱格式檢查
        description (str): 伺服器描述
        
    Returns:
        dict: 包含新增伺服器資訊的字典
        
    Raises:
        FileNotFoundError: 當指定的路徑不存在時
        ValueError: 當檔案類型不正確或資料夾命名格式不符合規範時
    """
    # 移除引號
    server_path = server_path.strip('"\'')

    def parse_folder_info(folder_name: str) -> dict:
        """解析資料夾名稱獲取伺服器信息"""
        # 使用非貪婪匹配（?）來處理名稱中的底線
        pattern = r'^(.+?)_(\d+\.\d+\.\d+)_(\d{4,5})_(fabric|forge|vanilla|paper|spigot)$'
        match = re.match(pattern, folder_name)
        if not match:
            return None
        return {
            "name": match.group(1),
            "version": match.group(2),
            "port": int(match.group(3)),
            "core_type": match.group(4)
        }

    # 檢查路徑是否存在
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"找不到指定的伺服器路徑：{server_path}")
    
    # 檢查是否為有效的啟動檔案
    if not server_path.lower().endswith(('.bat', '.sh')):
        raise ValueError("請選擇正確的啟動檔案（必須是 .bat 或 .sh 檔案）")
    
    # 只在非強制模式下檢查資料夾命名格式
    if not force and not parse_folder_info(Path(server_path).parent.name):
        raise ValueError(
            "資料夾名稱格式錯誤！\n"
            "正確格式為：伺服器名稱_版本號_端口號_核心類型\n"
            "範例：skywind_empire2_1.21.4_25560_fabric\n"
            "使用 -f 參數可略過此檢查"
        )
    
    # 確保配置目錄存在
    config_path = Path("config/server.json")
    config_path.parent.mkdir(exist_ok=True)

    # 讀取或創建配置文件
    if not config_path.exists():    
        data = {
            "servers": []
        }
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if "servers" not in data:
                    data["servers"] = []
            except json.JSONDecodeError:
                data = {
                    "servers": []
                }

    # 檢查路徑是否重複
    normalized_path = os.path.normpath(server_path)
    if any(server["path"] == normalized_path for server in data["servers"]):
        raise ValueError(f"此伺服器路徑已經存在：{normalized_path}")
    
    # 解析資料夾信息
    folder_info = parse_folder_info(Path(server_path).parent.name)
    if not folder_info and not force:
        raise ValueError(
            "資料夾名稱格式錯誤！\n"
            "正確格式為：伺服器名稱_版本號_端口號_核心類型\n"
            "範例：skywind_empire2_1.21.4_25560_fabric\n"
            "使用 -f 參數可略過此檢查"
        )

    # 創建新伺服器配置
    new_server = {
        "path": normalized_path,
        "name": folder_info["name"] if folder_info else Path(server_path).parent.name,
        "version": folder_info["version"] if folder_info else "unknown",
        "port": folder_info["port"] if folder_info else 0,
        "core_type": folder_info["core_type"] if folder_info else "unknown",
        "status": "stopped",
        "last_start": None,
        "last_stop": None,
        "description": description,
        "pid": None
    }
    
    # 添加新伺服器
    data["servers"].append(new_server)
    
    # 保存更新後的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 返回新增的伺服器資訊
    return new_server

async def remove_server(server_identifier: str) -> dict:
    """
    從配置文件中移除指定的 Minecraft 伺服器。
    
    Args:
        server_identifier (str): 伺服器標識符，格式為 "名稱_版本"
        
    Returns:
        dict: 被移除的伺服器資訊
        
    Raises:
        ValueError: 當找不到指定的伺服器或格式錯誤時
    """
    # 使用正則表達式解析伺服器標識符
    pattern = r'^(.+?)_(\d+\.\d+\.\d+)$'
    match = re.match(pattern, server_identifier)
    if not match:
        raise ValueError(
            "伺服器標識符格式錯誤！\n"
            "正確格式為：名稱_版本號\n"
            "範例：skywind_empire2_1.21.4\n"
            "注意：名稱可以包含底線，但版本號必須是 x.y.z 格式"
        )
    
    name = match.group(1)  # 取得伺服器名稱（可能包含底線）
    version = match.group(2)  # 取得版本號
    
    config_path = Path("config/server.json")
    
    if not config_path.exists():
        raise ValueError("還沒有任何伺服器被添加")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 尋找並移除伺服器
    server_to_remove = None
    for server in data["servers"]:
        if server["name"] == name and server["version"] == version:
            server_to_remove = server
            data["servers"].remove(server)
            break
    
    if not server_to_remove:
        raise ValueError(f"找不到名為 '{name}' 且版本為 '{version}' 的伺服器")
    
    # 保存更新後的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return server_to_remove


async def list_servers() -> list:
    """
    獲取所有已註冊的伺服器列表。
    
    Returns:
        list: 包含所有伺服器資訊的列表
    """
    config_path = Path("config/server.json")
    
    if not config_path.exists():
        return []
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("servers", [])
async def start_server(server_identifier: str) -> dict:
    """
    啟動指定的 Minecraft 伺服器。
    
    Args:
        server_identifier (str): 伺服器標識符，格式為 "名稱_版本"
        
    Returns:
        dict: 啟動的伺服器資訊
        
    Raises:
        ValueError: 當找不到指定的伺服器或啟動失敗時
    """
    pattern = r'^(.+?)_(\d+\.\d+\.\d+)$'
    match = re.match(pattern, server_identifier)
    if not match:
        raise ValueError("伺服器標識符格式錯誤！正確格式為：名稱_版本號")
    
    name, version = match.groups()
    
    # 讀取配置
    servers = await list_servers()
    server = next((s for s in servers if s["name"] == name and s["version"] == version), None)
    
    if not server:
        raise ValueError(f"找不到名為 '{name}' 且版本為 '{version}' 的伺服器")
    
    if server["status"] == "running":
        raise ValueError("伺服器已在運行中")
    
    try:
        # 啟動伺服器
        server_dir = os.path.dirname(server["path"])
        server_file = os.path.basename(server["path"])

        if server_file.endswith('.bat'):
            process = subprocess.Popen(
                [server_file],
                cwd=server_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:  # 如果是 .sh 檔案
            process = subprocess.Popen(
                ['bash', server_file],
                cwd=server_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

        # 等待一下確保進程已經啟動
        await asyncio.sleep(2)

        if process.poll() is not None:  # 如果進程已結束
            raise ValueError("伺服器進程無法啟動")

        # 獲取子進程 PID
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
        
        if not children:
            raise ValueError("無法找到 Minecraft 伺服器進程")
            
        # 使用最後一個子進程的 PID（通常是 Java 進程）
        server_pid = children[-1].pid
        
        # 關閉父進程（subprocess）
        parent.terminate()
        
        # 更新伺服器狀態，使用真實的伺服器 PID
        server["status"] = "running"
        server["last_start"] = datetime.now().isoformat()
        server["pid"] = server_pid

        # 保存配置
        config_path = Path("config/server.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for i, s in enumerate(data["servers"]):
            if s["name"] == name and s["version"] == version:
                data["servers"][i] = server
                break
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 發送桌面通知
        notification.notify(
            title="Minecraft 伺服器啟動",
            message=f"伺服器 {server['name']} ({server['version']}) 已成功啟動",
            timeout=5
        )
        
        # 啟動追踪
        asyncio.create_task(
            trace_server(server), 
            name=f"trace_{server['name']}_{server['version']}"
        )
        
        return server
        
    except Exception as e:
        raise ValueError(f"伺服器啟動失敗：{str(e)}")

async def stop_server(server_identifier: str) -> dict:
    """
    停止指定的 Minecraft 伺服器。
    
    Args:
        server_identifier (str): 伺服器標識符，格式為 "名稱_版本"
        
    Returns:
        dict: 停止的伺服器資訊
        
    Raises:
        ValueError: 當找不到指定的伺服器或停止失敗時
    """
    pattern = r'^(.+?)_(\d+\.\d+\.\d+)$'
    match = re.match(pattern, server_identifier)
    if not match:
        raise ValueError("伺服器標識符格式錯誤！正確格式為：名稱_版本號")
    
    name, version = match.groups()
    
    # 讀取配置
    servers = await list_servers()
    server = next((s for s in servers if s["name"] == name and s["version"] == version), None)
    
    if not server:
        raise ValueError(f"找不到名為 '{name}' 且版本為 '{version}' 的伺服器")
    
    if server["status"] != "running":
        raise ValueError("伺服器未在運行中")
    
    try:
        # 停止追踪
        for task in asyncio.all_tasks():
            if task.get_name() == f"trace_{server['name']}_{server['version']}":
                task.cancel()
        
        # 終止進程
        process = psutil.Process(server["pid"])
        process.terminate()
        
        # 等待進程終止
        process.wait()
        
        # 更新伺服器狀態
        server["status"] = "stopped"
        server["last_stop"] = datetime.now().isoformat()
        server["pid"] = None
        
        # 保存配置
        config_path = Path("config/server.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for i, s in enumerate(data["servers"]):
            if s["name"] == name and s["version"] == version:
                data["servers"][i] = server
                break
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 發送桌面通知
        notification.notify(
            title="Minecraft 伺服器停止",
            message=f"伺服器 {server['name']} ({server['version']}) 已成功停止",
            timeout=5
        )
        
        return server
        
    except Exception as e:
        raise ValueError(f"伺服器停止失敗：{str(e)}")

async def trace_server(server: dict) -> None:
    """
    追踪伺服器進程狀態。
    
    Args:
        server (dict): 伺服器配置信息
    """
    pid = server["pid"]
    name = server["name"]
    version = server["version"]
    
    logging.info(f"開始追踪伺服器 {name} ({version}) 進程 (PID: {pid})")
    
    while True:
        try:
            # 檢查進程是否存在
            process = psutil.Process(pid)
            if not process.is_running():
                raise ProcessLookupError
            
            # 等待一段時間再檢查
            await asyncio.sleep(5)
            
        except (ProcessLookupError, psutil.NoSuchProcess):
            # 進程已終止
            logging.info(f"伺服器 {name} ({version}) 進程已終止 (PID: {pid})")
            
            # 更新伺服器狀態
            server["status"] = "stopped"
            server["last_stop"] = datetime.now().isoformat()
            server["pid"] = None
            
            # 保存配置
            config_path = Path("config/server.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for i, s in enumerate(data["servers"]):
                if s["name"] == name and s["version"] == version:
                    data["servers"][i] = server
                    break
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 發送桌面通知
            notification.notify(
                title="Minecraft 伺服器已關閉",
                message=f"偵測到伺服器 {server['name']} ({server['version']}) 已停止運行",
                timeout=5
            )
            
            break

