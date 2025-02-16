from discord.ext import commands
import json
import logging
from pathlib import Path
import re

logger = logging.getLogger('bot')

class ServerList(commands.Cog, name="伺服器管理"):
    def __init__(self, bot):
        self.bot = bot
        logger.info('List 指令已初始化')

    @commands.command(name="list", description="列出所有可用的 Minecraft 伺服器")
    @commands.has_role('canOpenServer')
    async def list(self, ctx):
        """列出所有可用的伺服器"""
        try:
            with open('assets/servers.json', 'r', encoding='utf-8') as f:
                servers = json.load(f)['servers']
            
            server_list = "📋 自動偵測的伺服器列表：\n\n"
            
            for s in servers:
                try:
                    info = parse_server_info(s['path'])
                    start_cog = self.bot.get_cog('StartServer')
                    proc = start_cog.active_servers.get(info['name'])
                    is_active = proc is not None and proc.poll() is None
                    
                    status = "🟢 運行中" if is_active else "⚫ 關閉"
                    server_list += (
                        f"• {info['name']} ({status})\n"
                        f"  版本：{info['version']} | 端口：{info['port']} | 核心：{info['core']}\n"
                        f"  路徑：{s['path']}\n\n"
                    )
                except Exception as e:
                    logger.error(f"解析伺服器 {s['path']} 失敗：{e}")
            
            await ctx.send(server_list)
            
        except Exception as e:
            await ctx.send(f"❌ 取得列表失敗：{str(e)}")

async def setup(bot):
    await bot.add_cog(ServerList(bot))
    logger.info('List 指令已載入')

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