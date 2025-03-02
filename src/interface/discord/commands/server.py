import discord
from discord.ext import commands
from src.service import server_service
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()
DDNS = os.getenv('DDNS', 'localhost')

def setup(bot):
    """註冊所有伺服器相關指令"""
    bot.add_command(add_server)
    bot.add_command(remove_server)
    bot.add_command(list_servers)  # 改名為 list_servers 避免與內建 list 衝突
    bot.add_command(start)  # 新增
    bot.add_command(stop)   # 新增

@commands.command()
async def add_server(ctx, path: str, force: bool = False, *, description: str = None):
    """
    新增 Minecraft 伺服器
    
    參數：
    - path: 伺服器啟動檔案路徑
    - force: 是否略過資料夾名稱格式檢查 (可選)
    - description: 伺服器描述 (可選)
    """
    try:
        server = await server_service.add_server(path, force, description)
        
        # 建立嵌入訊息
        embed = discord.Embed(
            title="✅ 伺服器新增成功",
            color=discord.Color.green()
        )
        embed.add_field(name="名稱", value=server['name'], inline=True)
        embed.add_field(name="版本", value=server['version'], inline=True)
        embed.add_field(name="核心", value=server['core_type'], inline=True)
        embed.add_field(name="端口", value=str(server['port']), inline=True)
        if description:
            embed.add_field(name="描述", value=description, inline=False)
        embed.add_field(name="路徑", value=f"```{server['path']}```", inline=False)
        
        await ctx.send(embed=embed)
        
    except (FileNotFoundError, ValueError) as e:
        embed = discord.Embed(
            title="❌ 新增失敗",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ 發生未預期的錯誤",
            description=f"```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@commands.command()
async def remove_server(ctx, server_id: str):
    """
    移除 Minecraft 伺服器
    
    參數：
    - server_id: 伺服器識別碼 (格式：名稱_版本號)
    """
    try:
        removed_server = await server_service.remove_server(server_id)
        
        # 建立嵌入訊息
        embed = discord.Embed(
            title="✅ 伺服器移除成功",
            color=discord.Color.green()
        )
        embed.add_field(name="名稱", value=removed_server['name'], inline=True)
        embed.add_field(name="版本", value=removed_server['version'], inline=True)
        embed.add_field(name="核心", value=removed_server['core_type'], inline=True)
        embed.add_field(name="路徑", value=f"```{removed_server['path']}```", inline=False)
        
        await ctx.send(embed=embed)
        
    except ValueError as e:
        embed = discord.Embed(
            title="❌ 移除失敗",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ 發生未預期的錯誤",
            description=f"```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@commands.command(name='list')  # 使用 name 參數指定指令名稱
async def list_servers(ctx):
    """列出所有 Minecraft 伺服器"""
    servers = await server_service.list_servers()
    
    if not servers:
        embed = discord.Embed(
            title="📋 伺服器列表",
            description="目前還沒有註冊任何伺服器\n使用 `?add_server <路徑>` 來新增伺服器",
            color=discord.Color.light_grey()
        )
        await ctx.send(embed=embed)
        return

    # 建立主要訊息
    embed = discord.Embed(
        title="📋 伺服器列表",
        description=f"共有 {len(servers)} 個已註冊的伺服器",
        color=discord.Color.blue()
    )

    # 依核心類型分類
    servers_by_type = {}
    for server in servers:
        core_type = server.get('core_type', 'unknown')
        if core_type not in servers_by_type:
            servers_by_type[core_type] = []
        servers_by_type[core_type].append(server)

    # 顯示各類型伺服器
    for core_type, type_servers in servers_by_type.items():
        server_list = []
        connect_info = []
        
        for server in type_servers:
            status_emoji = '🟢' if server.get('status') == 'running' else '🔴'
            port_info = f":{server['port']}" if server.get('port') else ''
            desc = f" - {server['description']}" if server.get('description') else ''
            
            server_list.append(
                f"{status_emoji} **{server['name']}** "
                f"(`{server['version']}`{port_info}){desc}"
            )
            
            # 只為運行中的伺服器添加連線資訊
            if server.get('status') == 'running' and server.get('port'):
                connect_info.append(f"```{DDNS}:{server['port']}```")

        # 添加該核心類型的伺服器列表
        if server_list:
            embed.add_field(
                name=f"{core_type.capitalize()} 核心",
                value='\n'.join(server_list),
                inline=False
            )
            # 如果有運行中的伺服器，添加連線資訊
            if connect_info:
                embed.add_field(
                    name=f"{core_type.capitalize()} 連線地址",
                    value='\n'.join(connect_info),
                    inline=False
                )

    # 添加說明欄位
    embed.add_field(
        name="狀態說明",
        value="🟢 運行中 | 🔴 已停止",
        inline=False
    )
    
    # 添加使用提示
    embed.set_footer(
        text="使用 ?add_server [-f] [-d [description]] <path> 新增伺服器 | ?remove_server <名稱_版本>移除伺服器"
    )

    await ctx.send(embed=embed)

@commands.command()
async def start(ctx, server_identifier: str):
    """
    啟動指定的 Minecraft 伺服器
    
    參數：
    - server_identifier: 伺服器識別碼 (格式：名稱_版本號)
    """
    try:
        server = await server_service.start_server(server_identifier)
        
        # 建立嵌入訊息
        embed = discord.Embed(
            title="🚀 伺服器啟動中",
            description=f"正在啟動 {server['name']} ({server['version']}) 伺服器",
            color=discord.Color.green()
        )
        embed.add_field(name="核心", value=server['core_type'], inline=True)
        embed.add_field(name="端口", value=str(server['port']), inline=True)
        embed.add_field(name="PID", value=str(server['pid']), inline=True)
        
        # 如果設定了 DDNS，添加連線資訊
        if server['port']:
            embed.add_field(
                name="連線地址",
                value=f"```{DDNS}:{server['port']}```",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except ValueError as e:
        embed = discord.Embed(
            title="❌ 啟動失敗",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ 發生未預期的錯誤",
            description=f"```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@commands.command()
async def stop(ctx, server_identifier: str):
    """
    停止指定的 Minecraft 伺服器
    
    參數：
    - server_identifier: 伺服器識別碼 (格式：名稱_版本號)
    """
    try:
        server = await server_service.stop_server(server_identifier)
        
        # 建立嵌入訊息
        embed = discord.Embed(
            title="🛑 伺服器已停止",
            description=f"已成功停止 {server['name']} ({server['version']}) 伺服器",
            color=discord.Color.orange()
        )
        embed.add_field(name="核心", value=server['core_type'], inline=True)
        embed.add_field(name="端口", value=str(server['port']), inline=True)
        embed.add_field(
            name="運行時間",
            value=get_runtime_duration(server['last_start'], server['last_stop']),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except ValueError as e:
        embed = discord.Embed(
            title="❌ 停止失敗",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ 發生未預期的錯誤",
            description=f"```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

def get_runtime_duration(start_time: str, stop_time: str) -> str:
    """計算伺服器運行時間"""
    if not start_time or not stop_time:
        return "無法計算"
    
    try:
        start = datetime.fromisoformat(start_time)
        stop = datetime.fromisoformat(stop_time)
        duration = stop - start
        
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} 天")
        if hours > 0:
            parts.append(f"{hours} 小時")
        if minutes > 0:
            parts.append(f"{minutes} 分鐘")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} 秒")
            
        return " ".join(parts)
    except:
        return "計算錯誤"


