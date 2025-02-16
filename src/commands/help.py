import discord
from discord.ext import commands
import logging
import json
from pathlib import Path
import frontmatter
import re
from dotenv import load_dotenv

logger = logging.getLogger('bot')

class CustomHelp(commands.Cog, name="幫助指令"):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = None  # 禁用預設 help
        self.config = load_config()  # 使用新的設定載入方式
        self.wiki_base = self.config["wiki"]["base_url"]
        self.wiki_path = Path("assets/wiki")
        self.commands = self._load_commands()
        logger.info('自定義 help 指令已初始化')

    def _load_commands(self):
        """從 JSON 載入指令說明"""
        help_path = Path("assets/command_help")
        commands = []
        
        for file in help_path.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 驗證必要字段
                    required_fields = ['name', 'title', 'category', 'sections']
                    if not all(field in data for field in required_fields):
                        logger.warning(f"無效的指令文件格式：{file.name}")
                        continue
                    
                    commands.append({
                        'name': data['name'],
                        'title': data['title'],
                        'color': int(data.get('color', '0x7289DA'), 16),
                        'category': data['category'],
                        'sections': data['sections']
                    })
                    logger.info(f"已載入指令說明：{data['name']}")
            except Exception as e:
                logger.error(f"載入指令文件錯誤 {file}: {str(e)}")
        
        return commands

    def format_text(self, text, **kwargs):
        """簡單的文本格式化"""
        return text.format(**kwargs)

    WIKI_MAP = {
        'start': '01_指令/基礎/start',
        'alist': '01_指令/進階/alist'
    }

    async def send_help_embed(self, ctx, command_name):
        command = next((c for c in self.commands if c['name'] == command_name), None)
        if not command:
            return await ctx.send("❌ 找不到此指令說明")
        
        try:
            embed = discord.Embed(
                title=f"{command['title']}",
                color=command['color']
            )
            
            for section in command['sections']:
                content = section['content']
                # 處理陣列類型的內容
                if isinstance(content, list):
                    content = '\n'.join(content)
                embed.add_field(
                    name=section['title'],
                    value=content,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"生成幫助訊息錯誤：{str(e)}")
            await ctx.send("⚠️ 生成說明時發生錯誤")

    @commands.command(name='help', description='顯示幫助訊息')
    async def help_command(self, ctx, command_name: str = None):
        if command_name:
            await self.send_help_embed(ctx, command_name)
        else:
            # 顯示指令分類列表
            embed = discord.Embed(
                title="📚 指令系統總覽",
                description=f"使用 `{self.config['bot']['prefix']}help <指令名稱>` 查看詳細說明\n[GitHub 維基文件]({self.config['wiki']['base_url']})",
                color=0x7289DA
            )
            
            # 分類指令
            categories = {}
            for cmd in self.commands:
                category = cmd['category']
                categories.setdefault(category, []).append(cmd)
            
            # 添加分類欄位
            for cat, cmds in categories.items():
                embed.add_field(
                    name=f"🔹 {cat}類指令",
                    value='\n'.join([f"`!help {c['name']}` - {c['title']}" for c in cmds]),
                    inline=False
                )
            
            await ctx.send(embed=embed)

    @commands.command(name='wiki')
    async def wiki_command(self, ctx, page: str = None):
        if page:
            await ctx.send(f"🌐 [查看完整維基](https://your-wiki-site.com/{page})")
        else:
            await ctx.send("📚 [維基首頁](https://your-wiki-site.com)")

    async def send_command_help(self, ctx, command_name):
        """從 Wiki 載入單一指令說明"""
        command = next((c for c in self.commands if c['name'] == command_name), None)
        if not command:
            return await ctx.send(f"❌ 找不到指令：{command_name}")
        
        embed = discord.Embed(
            title=f"📖 {command['name']} 指令說明",
            description=command['brief'],
            color=0x00ff00
        )
        for detail in command['details']:
            if ':' in detail:
                title, content = detail.split(':', 1)
                embed.add_field(
                    name=title.strip(),
                    value=content.strip(),
                    inline=False
                )
        await ctx.send(embed=embed)

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot):
    await bot.add_cog(CustomHelp(bot))
    logger.info('自定義 help 指令已載入') 