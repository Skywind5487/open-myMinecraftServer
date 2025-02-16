from discord.ext import commands
import json
import logging
import os
from pathlib import Path
import re

logger = logging.getLogger('bot')

def parse_server_info(full_path):
    """
    解析路徑格式：.../名稱_版本_port_核心類型/StartServer.bat
    範例：生存伺服器_1.20_25561_fabric
    """
    path_obj = Path(full_path)
    
    # 獲取父資料夾名稱
    folder_name = path_obj.parent.name
    
    # 使用正則表達式解析
    pattern = r"^(?P<name>.+?)_(?P<version>\d+\.\d+\.?\d*)_(?P<port>\d+)_(?P<core>.+)$"
    match = re.match(pattern, folder_name)
    
    if not match:
        raise ValueError(f"路徑格式錯誤：{folder_name}，預期格式：名稱_版本_port_核心類型")
    
    return {
        "name": match.group("name"),
        "version": match.group("version"),
        "port": int(match.group("port")),
        "core": match.group("core"),
        "folder": str(path_obj.parent),
        "script": path_obj.name
    }

class AddServerCommands(commands.Cog):
    COMMAND_HELP = {
        "name": "addserver",
        "title": "新增伺服器",
        "category": "系統",
        "color": "0x3498DB",  # 藍色
        "description": "新增 Minecraft 伺服器到管理清單",
        "sections": [
            {
                "title": "參數格式",
                "content": ["path_to_bat"]
            },
            {
                "title": "路徑要求",
                "content": [
                    "必須是絕對路徑",
                    "需符合格式：.../名稱_版本_端口_核心/StartServer.bat",
                    "範例：D:\\MC\\生存伺服器_1.20_25561_fabric\\StartServer.bat"
                ]
            }
        ],
        "tips": [
            "用法: !addserver <bat檔案路徑>",
            "功能: 新增伺服器到管理清單",
            "權限需求: canOpenServer 身分組",
            "範例: !addserver D:\\MC\\skyworld_1.21.4_25560_fabric\\StartServer.bat"
        ]
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addserver")
    @commands.has_role('canOpenServer')
    async def add_server(self, ctx, path_to_bat: str):
        """新增伺服器到管理清單"""
        try:
            # 驗證路徑格式
            server_info = parse_server_info(path_to_bat)
            
            # 檢查檔案是否存在
            if not os.path.exists(path_to_bat):
                return await ctx.send("❌ 檔案不存在，請檢查路徑")
                
            if not path_to_bat.lower().endswith('.bat'):
                return await ctx.send("❌ 必須是 .bat 檔案")

            # 讀取並更新 servers.json
            servers_file = 'assets/servers.json'
            with open(servers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 檢查是否已存在
            if any(s['path'] == path_to_bat for s in data['servers']):
                return await ctx.send("⚠️ 此伺服器已存在於清單中")

            data['servers'].append({"path": path_to_bat})
            
            with open(servers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # 回覆成功訊息
            success_msg = (
                f"✅ 已成功新增伺服器！\n"
                f"名稱：{server_info['name']}\n"
                f"版本：{server_info['version']}\n"
                f"端口：{server_info['port']}\n"
                f"核心：{server_info['core']}"
            )
            await ctx.send(success_msg)
            
        except ValueError as e:
            await ctx.send(f"❌ 路徑格式錯誤：{str(e)}")
        except json.JSONDecodeError:
            await ctx.send("❌ 設定檔案格式錯誤")
        except Exception as e:
            logger.error(f"新增伺服器失敗：{e}", exc_info=True)
            await ctx.send("❌ 新增伺服器時發生未預期錯誤")

async def setup(bot):
    await bot.add_cog(AddServerCommands(bot))
    logger.info('AddServer 指令已載入') 