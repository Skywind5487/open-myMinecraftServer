import discord
from discord.ext import commands
import logging
import json
from pathlib import Path
import frontmatter
import re
from src.bot import config  # 直接使用主程式的設定

logger = logging.getLogger('bot')

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="📚 指令幫助系統",
            color=0x7289DA,
            description=(
                f"使用 `{self.context.prefix}help <指令名稱>` 查看詳細說明\n\n"
                "⚠️ 部分指令需要 `canOpenServer` 身分組權限\n"
                "請聯繫管理員取得權限後使用"
            )
        )

        # 分類收集指令
        categories = {}
        for cog in self.context.bot.cogs.values():
            if hasattr(cog, 'COMMAND_HELP'):
                category = cog.COMMAND_HELP.get('category', '其他')
                categories.setdefault(category, []).append(cog)

        # 修改後
        category_order = ['基礎', '進階', '系統', '其他']
        for category in category_order:
            if category in categories:
                cogs = categories[category]
                value = []
                for cog in cogs:
                    help_info = cog.COMMAND_HELP
                    # 顯示完整 tips
                    tips_text = '\n'.join([f"{t}" for t in help_info.get('tips', [])])
                    value.append(
                        f"**{help_info.get('title', '未命名指令')}**\n"
                        f"{tips_text}\n"
                    )
                
                embed.add_field(
                    name=f"🔹 {category}類指令",
                    value='\n'.join(value),
                    inline=False
                )

        # 在最後添加額外說明
        embed.add_field(
            name="ℹ️ 其他資訊",
            value=(
                "👤 點擊我的頭像選擇「應用程式資訊」查看機器人基本資料\n\n"
                f"📚 完整使用手冊：[wiki](<{self.context.bot.config['wiki']['base_url']}>)"
            ),
            inline=False
        )

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        cog = command.cog
        if not cog or not hasattr(cog, 'COMMAND_HELP'):
            return await super().send_command_help(command)

        help_data = cog.COMMAND_HELP
        embed = discord.Embed(
            title=f"📖 {help_data.get('title', '指令說明')}",
            color=int(help_data.get('color', '0xFFFFFF'), 16),
            description=help_data.get('description', '暫無詳細說明')
        )

        # 修改後的指令格式欄位
        if 'name' in help_data:
            # 從 sections 中尋找參數說明
            params_section = next((s for s in help_data.get('sections', []) 
                                 if s.get('title') == '參數格式'), None)
            
            # 組合參數文字
            params_text = ""
            if params_section:
                params_text = ' '.join([f"<{p}>" for p in params_section.get('content', [])])
            
            embed.add_field(
                name="📝 指令格式",
                value=f"`{self.context.prefix}{help_data['name']} {params_text}`".strip(),
                inline=False
            )

        for section in help_data.get('sections', []):
            embed.add_field(
                name=section.get('title', '其他資訊'),
                value='\n'.join(section.get('content', ['暫無內容'])),
                inline=False
            )

        await self.get_destination().send(embed=embed)

async def setup(bot):
    bot.help_command = CustomHelp()
    logger.info('自定義 help 指令已載入') 