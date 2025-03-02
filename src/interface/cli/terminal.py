import asyncio
from .handler import handle_terminal_command, get_available_commands

class TerminalInterface:
    def __init__(self):
        self.running = True
        self._print_welcome()

    def _print_welcome(self):
        """顯示歡迎訊息"""
        print("\n=== Minecraft 伺服器管理系統 (終端機模式) ===")
        print("輸入 'help' 查看可用指令")
        print("按 Ctrl+C 結束程式")
        print("="*45)
        
        # 顯示已載入的指令
        print("\n已載入的指令：")
        for cmd, desc in get_available_commands().items():
            print(f"  {cmd:15} - {desc}")
        print("\n")

    async def run(self):
        """運行終端機介面"""
        while self.running:
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: input("[終端機] > ").strip()
                )
                if command:
                    if not await handle_terminal_command(command):
                        break
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"錯誤：{e}")
        
        print("[終端機模式] 已關閉")
