import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from interface.discord.bot import MinecraftBot
from interface.cli.terminal import TerminalInterface

async def setup_environment():
    """設置運行環境"""
    load_dotenv()
    Path("config").mkdir(exist_ok=True)

async def _main():
    """異步主程式"""
    await setup_environment()
    
    mode = "--both"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    terminal = None
    bot = None
    tasks = []

    try:
        if mode in ["--both", "--terminal"]:
            terminal = TerminalInterface()
            tasks.append(asyncio.create_task(terminal.run()))
            
        if mode in ["--both", "--discord"]:
            bot = MinecraftBot()
            tasks.append(asyncio.create_task(bot.run()))
            
        if not tasks:
            print("無效的啟動模式！可用選項：")
            print("  --terminal  : 僅終端機模式")
            print("  --discord   : 僅 Discord 模式")
            print("  --both/無參數: 雙介面模式")
            return

        # 等待任意任務結束
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

    except KeyboardInterrupt:
        print("\n正在關閉系統...")
    finally:
        # 關閉所有介面
        for task in tasks:
            if not task.done():
                task.cancel()
        
        if terminal:
            terminal.running = False
        if bot:
            bot.running = False
            
        await asyncio.gather(*tasks, return_exceptions=True)
        print("系統已完全關閉")

def main():
    """程式入口點"""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()