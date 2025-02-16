from discord.ext import commands
import logging

logger = logging.getLogger('bot')

class Ping(commands.Cog, name="基本指令"):
    def __init__(self, bot):
        self.bot = bot
        logger.info('Ping 指令已初始化')

    @commands.command(
        name="ping",
        description="測試機器人的回應延遲",
        help="顯示機器人與 Discord 伺服器之間的延遲"
    )
    async def ping(self, ctx):
        try:
            latency = round(self.bot.latency * 1000)
            await ctx.send(f'🏓 延遲：{latency}ms')
            logger.info(f"Ping 指令執行成功：{latency}ms")
        except Exception as e:
            logger.error(f"Ping 指令錯誤：{e}")
            await ctx.send("❌ 無法取得延遲資訊")

async def setup(bot):
    await bot.add_cog(Ping(bot))
    logger.info('Ping 指令已載入')