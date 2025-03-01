import discord
from discord.ext import commands
import logging
from ..services.server import MinecraftServer

logger = logging.getLogger(__name__)

class MinecraftCommands(commands.Cog, name="Minecraft"):
    """Minecraft 伺服器管理指令"""

    def __init__(self, bot, server: MinecraftServer):
        self.bot = bot
        self.server = server
        logger.info("Minecraft指令模組已載入")

    @commands.command(name="ping", help="檢查機器人延遲")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        logger.info(f"Ping 指令回應: {latency}ms")
        await ctx.send(f"🏓 Pong! ({latency}ms)")

    @commands.command(name="start", help="啟動 Minecraft 伺服器")
    async def start(self, ctx):
        logger.info("執行啟動伺服器指令")
        if await self.server.start():
            embed = discord.Embed(
                title="✅ 伺服器啟動中",
                description="Minecraft 伺服器正在啟動...",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 啟動失敗",
                description="伺服器可能已在運行中或發生錯誤",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @commands.command(name="stop", help="關閉 Minecraft 伺服器")
    async def stop(self, ctx):
        logger.info("執行關閉伺服器指令")
        if await self.server.stop():
            embed = discord.Embed(
                title="✅ 伺服器已停止",
                description="Minecraft 伺服器已成功關閉",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 停止失敗",
                description="伺服器可能未運行或發生錯誤",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @commands.command(name="status", help="查看伺服器狀態")
    async def status(self, ctx):
        logger.info("執行查詢伺服器狀態指令")
        status = await self.server.get_status()
        
        if status["status"] == "online":
            logger.info(f"伺服器在線中 - PID: {status['pid']}, CPU: {status['cpu_usage']:.1f}%, MEM: {status['memory_usage']:.1f}%")
            embed = discord.Embed(
                title="🟢 伺服器狀態",
                color=discord.Color.green()
            )
            embed.add_field(name="PID", value=str(status['pid']))
            embed.add_field(name="CPU 使用率", value=f"{status['cpu_usage']:.1f}%")
            embed.add_field(name="記憶體使用率", value=f"{status['memory_usage']:.1f}%")
        else:
            logger.info("伺服器離線中")
            embed = discord.Embed(
                title="🔴 伺服器離線中",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
