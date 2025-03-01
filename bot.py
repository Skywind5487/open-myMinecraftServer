import discord
from discord.ext import commands
import dotenv
from dotenv import load_dotenv
import os

load_dotenv()

def create_bot():
    bot = commands.Bot(
        command_prefix=os.getenv('DISCORD_PREFIX'),
        intents=discord.Intents.all()
    )
    
    # 載入指令
    from src.command.server import add_server
    bot.add_command(add_server)
    
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name} - {bot.user.id}')
        print('------')
        print('已載入的指令：', end='')
        command_names = [command.name for command in bot.commands]
        print(', '.join(command_names))
        print('------')
    
    return bot

if __name__ == "__main__":
    bot = create_bot()
    bot.run(os.getenv('DISCORD_TOKEN'))