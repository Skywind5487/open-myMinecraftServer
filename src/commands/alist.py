from discord.ext import commands
import discord
from src.utils import load_config

class AListCommands:
    @commands.command()
    async def alist(self, ctx):
        config = load_config()
        embed = discord.Embed(title="雲端管理資訊")
        embed.add_field(
            name="檔案路徑",
            value=f"[雲端管理入口]({config['wiki']['base_url']}/%E9%9B%B2%E7%AB%AF%E7%AE%A1%E7%90%86.md)"
        )
        await ctx.send(embed=embed) 