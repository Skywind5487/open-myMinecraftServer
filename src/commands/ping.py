from discord.ext import commands
import logging

logger = logging.getLogger('bot')

class Ping(commands.Cog, name="基本指令"):
    COMMAND_HELP = {
        "name": "ping",
        "title": "延遲檢測",
        "category": "系統",
        "color": "0x00FF00",  # 亮綠色
        "description": "測量機器人與 Discord 伺服器的通訊延遲",
        "sections": [
            {
                "title": "參數格式",
                "content": []  # 無參數
            },
            {
                "title": "技術規格",
                "content": [
                    "測量 WebSocket 延遲時間",
                    "精度：毫秒級 (ms)"
                ]
            },
            {
                "title": "使用情境",
                "content": [
                    "檢查機器人連線狀態",
                    "網路問題診斷"
                ]
            }
        ],
        "tips": [
            "用法: !ping",
            "功能: 檢測機器人與 Discord 延遲",
            "正常值應在 50-300ms 之間"
        ]
    }

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
            await ctx.send(f"Pong! {latency}ms")
            logger.info(f"Ping 指令執行成功：{latency}ms")
        except Exception as e:
            logger.error(f"Ping 指令錯誤：{e}")
            await ctx.send("❌ 無法取得延遲資訊")

async def setup(bot):
    await bot.add_cog(Ping(bot))
    logger.info('Ping 指令已載入')