from discord.ext import commands
import discord
from src.utils import load_config
import logging

logger = logging.getLogger(__name__)

class AListCommands(commands.Cog):
    COMMAND_HELP = {
        "name": "alist",
        "title": "雲端儲存系統",
        "category": "進階",
        "color": "0x9B59B6",  # 紫水晶色
        "description": "管理玩家存檔的雲端儲存服務",
        "sections": [
            {
                "title": "參數格式",
                "content": []  # 無參數
            },
            {
                "title": "連線資訊",
                "content": [
                    "HTTP/HTTPS 雙協議支援",
                    "自動整合 DDNS 設定"
                ]
            },
            {
                "title": "安全機制",
                "content": [
                    "密碼採用 Discord 原生模糊處理",
                    "連線逾時設定：30 秒"
                ]
            }
        ],
        "tips": [
            "用法: !alist",
            "功能: 顯示雲端儲存連線資訊",
            "密碼點擊後可查看完整內容",
            "網址自動整合 DDNS 設定"
        ]
    }

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def alist(self, ctx):
        """顯示 Alist 雲端儲存資訊"""
        config = self.bot.config.get("network", {}).get("alist", {})
        ddns_host = self.bot.config.get("network", {}).get("ddns", "")
        
        # 在解析 URL 前加入安全檢查
        if not isinstance(config, dict):
            return await ctx.send("❌ 設定格式錯誤")
        
        # 在最後加入例外處理
        try:
            required_fields = ["url", "http_port", "https_port", "username", "password"]
            missing = [field for field in required_fields if not config.get(field)]
            if missing:
                return await ctx.send(f"❌ Alist 設定不完整，缺少：{', '.join(missing)}")
            
            # 使用 DDNS 主機名稱
            base_url = ddns_host if ddns_host else config['url']
            base_url = base_url.split("://")[-1].split(":")[0]  # 移除協議和端口
            
            # 取得指令顏色設定
            color = discord.Color.from_str(
                self.bot.config.get("command_colors", {}).get("alist", "#7289da")
            )

            embed = discord.Embed(
                title="📁 Alist 雲端儲存管理系統",
                color=color,
                description="以下為雲端儲存服務的連線資訊："
            )
            
            # 修正後的服務器地址欄位
            embed.add_field(
                name="🌐 服務器地址",
                value=(
                    f"HTTP: \n"
                    f"```\n"
                    f"http://{base_url}:{config['http_port']}\n"
                    f"```\n"
                    f"HTTPS : \n"
                    f"```\n"
                    f"https://{base_url}:{config['https_port']}\n"
                    f"```"
                ),
                inline=False
            )

            embed.add_field(
                name="🔑 登入憑證",
                value=(
                    f"帳號: \n"
                    f"```\n"
                    f"{config['username']}\n"
                    f"```\n"
                    f"密碼: \n"
                    f"||{config['password']}||\n"
                ),
                inline=False
            )
            
            embed.set_footer(text="⚠️ 密碼已隱藏處理，點擊即可查看")
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"執行 alist 指令失敗: {e}")
            await ctx.send("❌ 取得雲端資訊時發生錯誤")

async def setup(bot):
    await bot.add_cog(AListCommands(bot))
    print('AList 指令已載入') 