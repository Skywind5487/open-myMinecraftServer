import discord
from discord.ext import commands
import json
import os

def setup(bot):
    bot.add_command(list_servers)

@commands.command(name='list')
async def list_servers(ctx: commands.Context):
    """
    Discord 指令: 列出所有已添加的 Minecraft 伺服器
    """
    config_path = "config/server.json"
    
    if not os.path.exists(config_path):
        await ctx.send("找不到伺服器設定檔！")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        servers = data.get("servers", [])  # 從 "servers" 鍵獲取伺服器列表
    
    if not servers:
        await ctx.send("目前還沒有新增任何 Minecraft 伺服器！")
        return
    
    embed = discord.Embed(
        title="Minecraft 伺服器清單",
        color=discord.Color.green()
    )
    
    for server in servers:
        name = server.get("name", "未命名伺服器")
        status = server.get("status", "offline")
        port = server.get("port", "N/A")
        core_type = server.get("core_type", "N/A")
        version = server.get("version", "N/A")
        
        status_icon = "🟢" if status == "online" else "🔴"
        status_text = "在線" if status == "online" else "離線"
        
        embed.add_field(
            name=f"📍 {name} {status_icon}",
            value=
                f"Port: {port}\n"
                f"核心類型: {core_type}\n"
                f"版本: {version}\n"
                f"狀態: {status_text}",
            inline=False
        )
    
    await ctx.send(embed=embed)