import discord
from discord.ext import commands
from src.service.server_backend import add_server as backend_add_server

@commands.command(name='add_server')
async def add_server(ctx, server_path: str):
    if not server_path:
        await ctx.send('Please provide a server path.')
        return

    try:
        await backend_add_server(server_path)
        await ctx.send('Server added!')
    except FileNotFoundError:
        await ctx.send('Server path not found. Please check the path and try again.')
    except Exception as e:
        await ctx.send(f'Error adding server: {e}')