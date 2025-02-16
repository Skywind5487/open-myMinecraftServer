from discord.ext import commands

class MockAListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def alist(self, ctx):
        embed = discord.Embed(title="雲端管理資訊 (測試用)")
        await ctx.send(embed=embed) 