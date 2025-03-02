from .server import setup as setup_server_commands
def setup():
    """設定所有 Discord 指令"""
    all_commands = []
    all_commands.extend(setup_server_commands())
    return all_commands