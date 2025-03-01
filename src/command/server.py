import discord
from discord.ext import commands
from src.service.server_backend import add_server as backend_add_server, remove_server as backend_remove_server
import os
from dotenv import load_dotenv

@commands.command(name='add_server')
async def add_server(ctx, *args):
    """
    Discord 指令: 添加新的 Minecraft 伺服器
    
    用法: !add_server [-f] <伺服器啟動檔路徑>
    
    Args:
        ctx: Discord 命令上下文
        args: 命令參數，可包含 -f 選項和伺服器路徑
    """
    force = False
    server_path = None
    
    # 解析參數
    for arg in args:
        if (arg == '-f'):
            force = True
        else:
            server_path = arg

    if not server_path:
        await ctx.send('請提供伺服器路徑')
        return

    try:
        server_info = await backend_add_server(server_path, force=force)
        
        # 載入 DDNS 設定
        load_dotenv()
        ddns = os.getenv('DDNS', 'localhost')
        server_address = f"{ddns}:{server_info['port']}"
        
        embed = discord.Embed(
            title="✅ 伺服器新增成功！",
            color=discord.Color.green(),
            description=f"已將以下伺服器添加到管理列表："
        )
        embed.add_field(name="伺服器名稱", value=server_info["name"], inline=True)
        embed.add_field(name="版本", value=server_info["version"], inline=True)
        embed.add_field(name="核心類型", value=server_info["core_type"], inline=True)
        embed.add_field(name="端口", value=str(server_info["port"]), inline=True)
        embed.add_field(
            name="連線位址 (點擊複製)", 
            value=f"```{server_address}```", 
            inline=True
        )
        embed.add_field(name="路徑", value=f"`{server_info['path']}`", inline=False)

        if force:
            embed.set_footer(text="注意：使用了強制模式 (-f) 添加")
        
        await ctx.send(embed=embed)
    except FileNotFoundError:
        await ctx.send('❌ 找不到指定的伺服器路徑，請確認路徑是否正確')
    except Exception as e:
        await ctx.send(f'❌ 新增伺服器時發生錯誤：{e}')

@commands.command(name='rm_server')
async def remove_server(ctx, server_identifier: str = None):
    """
    Discord 指令: 移除 Minecraft 伺服器
    
    用法: !rm_server <伺服器名稱_版本>
    範例: !rm_server skywind_empire2_1.21.4
    
    Args:
        ctx: Discord 命令上下文
        server_identifier: 伺服器標識符 (格式: 名稱_版本)
    """
    if not server_identifier:
        await ctx.send('❌ 請提供要移除的伺服器標識符 (格式: 名稱_版本)')
        return

    try:
        removed_server = await backend_remove_server(server_identifier)
        
        embed = discord.Embed(
            title="🗑️ 伺服器移除成功！",
            color=discord.Color.orange(),
            description=f"已將以下伺服器從管理列表中移除："
        )
        embed.add_field(name="伺服器名稱", value=removed_server["name"], inline=True)
        embed.add_field(name="版本", value=removed_server["version"], inline=True)
        embed.add_field(name="核心類型", value=removed_server["core_type"], inline=True)
        embed.add_field(name="端口", value=str(removed_server["port"]), inline=True)
        embed.add_field(name="路徑", value=f"`{removed_server['path']}`", inline=False)
        
        await ctx.send(embed=embed)
    except ValueError as e:
        await ctx.send(f'❌ {str(e)}')
    except Exception as e:
        await ctx.send(f'❌ 移除伺服器時發生錯誤：{e}')


