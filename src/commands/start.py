# Poetry 開發依賴：
# 測試時可安裝：poetry add --group dev pytest
# 運行測試：poetry run pytest tests/

from discord.ext import commands
import subprocess
import json
import os
from plyer import notification
import logging
import psutil  # 新增依賴，需安裝
import asyncio
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def send_desktop_notification(title, message):
    try:
        notification.notify(
            title=f"[MC Server Bot] {title}",
            message=f"{message}\n\n來自 open-myMinecraftServer 系統通知",
            app_name='MC Server Controller',
            timeout=15,
            toast=True
        )
        logger.info(f"系統通知已發送：{title}")
    except Exception as e:
        logger.error(f"通知發送失敗：{str(e)}")

def parse_server_info(full_path):
    """
    解析路徑格式：.../名稱_版本_port_核心類型/StartServer.bat
    範例：skywind_empire2_1.21.4_25560_fabric
    """
    path_obj = Path(full_path)
    
    # 獲取父資料夾名稱
    folder_name = path_obj.parent.name
    
    # 使用正則表達式解析
    pattern = r"^(?P<name>.+?)_(?P<version>\d+\.\d+\.\d+)_(?P<port>\d+)_(?P<core>.+)$"
    match = re.match(pattern, folder_name)
    
    if not match:
        raise ValueError(
            f"路徑格式錯誤：{folder_name}\n"
            "正確格式應為：名稱_三位版本號_端口_核心類型\n"
            "範例：skywind_empire2_1.21.4_25560_fabric"
        )
    
    return {
        "name": match.group("name"),
        "version": match.group("version"),
        "port": int(match.group("port")),
        "core": match.group("core"),
        "folder": str(path_obj.parent),
        "script": path_obj.name
    }

class StartServer(commands.Cog):
    COMMAND_HELP = {
        "name": "start",
        "title": "伺服器啟動",
        "category": "基礎",
        "color": "0x00FF00",  # 亮綠色
        "description": "啟動指定的 Minecraft 伺服器實例",
        "sections": [
            {
                "title": "參數格式",
                "content": [
                    "伺服器名稱_版本"
                ]
            },
            {
                "title": "注意事項",
                "content": [
                    "需要 'canOpenServer' 角色權限",
                    "啟動過程約需 1-3 分鐘",
                    "⚠️ 若無權限請聯繫管理員取得"
                ]
            }
        ],
        "tips": [
            "用法: !start <伺服器名稱_版本>",
            "功能: 啟動指定版本 Minecraft 伺服器",
            "權限需求: canOpenServer 身分組",
            "範例: !start skyworld_1.21.4"
        ]
    }
    
    def __init__(self, bot):
        self.bot = bot
        self.active_servers = {}
        self.checker_task = self.bot.loop.create_task(self.check_server_status())

    async def check_server_status(self):
        """定時檢查伺服器狀態"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                for name, proc in list(self.active_servers.items()):
                    if proc.poll() is not None:
                        del self.active_servers[name]
                        logger.info(f"伺服器 {name} 已停止")
                        send_desktop_notification('伺服器關閉', f'{name} 已停止運行')
            except Exception as e:
                logger.error(f"狀態檢查錯誤: {e}")
            await asyncio.sleep(60)

    @commands.command()
    @commands.has_role('canOpenServer')
    async def start(self, ctx, *, name_version: str):
        """啟動伺服器 (格式：名稱_版本)"""
        try:
            # 解析輸入格式
            if '_' not in name_version:
                return await ctx.send("❌ 格式錯誤！請使用「名稱_版本」格式，例如：生存伺服器_1.20")
            
            input_name, input_version = name_version.rsplit('_', 1)
            
            # 讀取並匹配伺服器
            with open('assets/servers.json', 'r', encoding='utf-8') as f:
                servers = json.load(f)['servers']
            
            # 讀取全局配置
            with open('assets/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            matched = []
            for s in servers:
                try:
                    info = parse_server_info(s['path'])
                    if (input_name in info['name'] and 
                        input_version == info['version']):
                        matched.append(s['path'])
                except Exception as e:
                    logger.error(f"解析失敗：{s['path']} - {e}")
            
            if not matched:
                return await ctx.send("❌ 找不到符合的伺服器")
            if len(matched) > 1:
                return await ctx.send(f"❌ 找到多個匹配伺服器，請明確指定：\n" + "\n".join(matched))
            
            full_path = matched[0]
            server_info = parse_server_info(full_path)
            
            if server_info['name'] in self.active_servers:
                proc = self.active_servers[server_info['name']]
                if proc.poll() is None:  # 進程仍在運行
                    return await ctx.send("⚠️ 伺服器已在運行中")
                else:  # 進程已結束但未清理
                    del self.active_servers[server_info['name']]
            
            try:
                # 檢查啟動腳本是否存在
                script_path = os.path.join(server_info['folder'], server_info['script'])
                logger.info(f"檢查啟動腳本路徑：{script_path}")
                print(f"[DEBUG] 腳本路徑：{script_path}")
                print(f"[DEBUG] 檔案是否存在：{os.path.exists(script_path)}")
                if not os.path.exists(script_path):
                    logger.error(f"啟動腳本不存在：{script_path}")
                    return await ctx.send(f"❌ 找不到啟動腳本：{script_path}")
                
                # 啟動伺服器
                proc = subprocess.Popen(
                    ['cmd.exe', '/k', full_path],
                    cwd=server_info['folder'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                self.active_servers[server_info['name']] = proc
                
                # 發送成功訊息，包含連線資訊
                success_msg = (
                    f"✅ {server_info['name']} 啟動成功！\n"
                    f"📌 連線位址：{config['DDNS']}:{server_info['port']}\n"
                    f"⚡ 版本：{server_info['version']} | 核心：{server_info['core']}"
                )
                await ctx.send(success_msg)
                
                # 發送系統通知
                send_desktop_notification('伺服器啟動通知', f'{server_info['name']} 已成功啟動')
                
            except Exception as e:
                await ctx.send(f"❌ 啟動失敗：{str(e)}")
                logger.error(f"啟動過程錯誤：{e}", exc_info=True)
        except Exception as e:  # 新增最外層的 except
            await ctx.send(f"❌ 發生未預期錯誤：{str(e)}")
            logger.error(f"start 指令未處理錯誤：{e}", exc_info=True)


async def setup(bot):
    await bot.add_cog(StartServer(bot))
    logger.info('Start 指令已載入') 
