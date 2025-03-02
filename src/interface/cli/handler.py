from pathlib import Path
from .commands.server import handle_list, handle_add_server, handle_remove_server

__all__ = ['handle_terminal_command', 'get_available_commands']

def get_available_commands():
    from .commands import setup
    all_commands = setup()
    all_commands.append(show_help)
    return {command.__name__.replace('handle_', ''): '顯示此幫助' if command == show_help else command.__name__.replace('handle_', '') for command in all_commands}

async def handle_terminal_command(command: str) -> bool:
    if not command:
        return True

    parts = command.split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    from .commands import setup
    all_commands = setup()
    all_commands.append(show_help)
    
    commands = {command.__name__.replace('handle_', ''): command for command in all_commands}
    commands.update({
        'exit': lambda: False,
        'quit': lambda: False
    })

    if cmd in commands:
        return await commands[cmd](*args) if args else await commands[cmd]()
    
    print(f"未知指令：{cmd}")
    return True

def show_help():
    print("""
可用指令：
  help - 顯示此幫助
  list - 顯示伺服器列表
  add_server [-f] [-d 描述] <路徑> - 新增伺服器
  remove_server <名稱_版本> - 移除伺服器
  exit/quit - 退出程式
    """)
    return True