import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys
import asyncio
from src.cli import handle_terminal_command

load_dotenv()

class MinecraftBot:
    def __init__(self):
        """初始化 Minecraft 伺服器管理機器人"""
        self.bot = commands.Bot(
            command_prefix=os.getenv('DISCORD_PREFIX'),
            intents=discord.Intents.all()
        )
        self.setup_commands()
        self.running = True
    
    def setup_commands(self):
        """設定 Discord 指令"""
        from src.command.server import add_server, remove_server
        import src.command.list as list_module
        
        list_module.setup(self.bot)
        self.bot.add_command(add_server)
        self.bot.add_command(remove_server)
        
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user.name} - {self.bot.user.id}')
            print('------')
            print('已載入的指令：', end='')
            command_names = [command.name for command in self.bot.commands]
            print(', '.join(command_names))
            print('------')
    
    async def input_handler(self):
        """處理終端機輸入的異步處理器"""
        while self.running:
            try:
                # 使用 run_in_executor 來非阻塞方式讀取輸入
                command = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    input, 
                    "\n> "
                )
                should_continue = await handle_terminal_command(command)
                if not should_continue:
                    self.running = False
                    await self.bot.close()
                    break
            except Exception as e:
                print(f"終端機指令錯誤：{e}")
    
    async def start_bot(self):
        """啟動 Discord Bot"""
        try:
            await self.bot.start(os.getenv('DISCORD_TOKEN'))
        except Exception as e:
            print(f"Discord bot 啟動失敗：{e}")
            if not os.getenv('DISCORD_TOKEN'):
                print("錯誤：找不到 DISCORD_TOKEN，請確認 .env 檔案設定")
            self.running = False
    
    async def run(self, terminal_mode=True):
        """運行機器人"""
        try:
            if terminal_mode:
                # 建立兩個異步任務
                terminal_task = asyncio.create_task(self.input_handler())
                discord_task = asyncio.create_task(self.start_bot())
                
                # 等待任一任務完成
                await asyncio.gather(terminal_task, discord_task)
            else:
                # 僅運行 Discord Bot
                await self.start_bot()
        except KeyboardInterrupt:
            print("\n正在關閉系統...")
        finally:
            self.running = False
            if self.bot:
                await self.bot.close()

async def main():
    """主程式入口"""
    mc_bot = MinecraftBot()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--terminal":
            # 僅終端機模式
            print("=== Minecraft 伺服器管理系統 (終端機模式) ===")
            await mc_bot.input_handler()
        elif sys.argv[1] == "--discord":
            # 僅 Discord bot 模式
            print("=== Minecraft 伺服器管理系統 (Discord 模式) ===")
            await mc_bot.run(terminal_mode=False)
        else:
            print("無效的參數！可用選項：")
            print("  --terminal  : 僅使用終端機模式")
            print("  --discord   : 僅使用 Discord bot 模式")
            print("  無參數      : 同時使用兩種模式")
            return
    else:
        # 同時運行兩個模式
        print("=== Minecraft 伺服器管理系統 (混合模式) ===")
        await mc_bot.run()

if __name__ == "__main__":
    asyncio.run(main())