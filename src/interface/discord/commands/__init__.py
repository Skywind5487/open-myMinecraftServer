from .server import setup as setup_server_commands

def setup(bot):
    """設定所有 Discord 指令"""
    setup_server_commands(bot)