import os
import discord
from discord.ext import commands
import asyncio

class MinecraftBot:
    def __init__(self):
        self.bot = commands.Bot(
            command_prefix=os.getenv('DISCORD_PREFIX', '!'),
            intents=discord.Intents.all()
        )
        self.running = True
        self.setup_commands()

    def setup_commands(self):
        @self.bot.event
        async def on_ready():
            print("\n=== Minecraft 伺服器管理系統 (Discord 模式) ===")
            print(f"Bot名稱: {self.bot.user.name}")
            print(f"Bot ID: {self.bot.user.id}")
            print(f"指令前綴: {self.bot.command_prefix}")
            print("="*45 + "\n")

        # 載入指令模組
        try:
            from .commands import setup
            setup(self.bot)
            # 加入調試訊息，從bot的指令列表顯示已載入的指令
            print("discord bot已載入指令：[", end="")
            for command in self.bot.commands:
                print(f"{command.name}", end=", ")
            print("]")

            print("Discord 指令載入完成")
        except Exception as e:
            print(f"載入 Discord 指令失敗：{str(e)}")
            import traceback
            print(traceback.format_exc())

    async def run(self):
        """運行 Discord Bot"""
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("錯誤：未設定 DISCORD_TOKEN")
            self.running = False
            return

        try:
            await self.bot.start(token)
        except discord.LoginFailure:
            print("錯誤：Discord 登入失敗，請檢查 Token")
        except asyncio.CancelledError:
            await self.bot.close()
        except Exception as e:
            print(f"Discord Bot 發生錯誤：{e}")
            
        finally:
            self.running = False
            print("[Discord 模式] 已關閉")
