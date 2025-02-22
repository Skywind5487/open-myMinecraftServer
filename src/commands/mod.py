import discord
from discord.ext import commands
import json
import logging
import os
import subprocess
import zipfile
import json
from pathlib import Path
from plyer import notification

logger = logging.getLogger('bot')

class ModCommands(commands.Cog):
    COMMAND_HELP = {
        "name": "mod",
        "title": "模組管理",
        "category": "進階",
        "color": "0x9b59b6",
        "description": "管理 Minecraft 伺服器模組",
        "sections": [
            {
                "title": "子指令列表",
                "content": [
                    "add <伺服器_版本> <URL> - 下載模組",
                    "disabled/enable <伺服器_版本> <模組名> - 停用/啟用模組",
                    "list update <伺服器_版本> - 更新模組清單",
                    "list <伺服器_版本> - 顯示模組清單"
                ]
            }
        ],
        "tips": [
            "需在伺服器關閉狀態下操作",
            "支援 .jar 和 .disabled 副檔名"
        ]
    }

    def __init__(self, bot):
        self.bot = bot

    def get_server_path(self, server_version):
        try:
            server_name, version = server_version.rsplit('_', 1)
        except ValueError:
            return None
        
        with open('assets/servers.json') as f:
            servers = json.load(f)['servers']
        
        for s in servers:
            path = Path(s['path'])
            folder = path.parent.name
            if f"{server_name}_{version}" in folder:
                return path.parent / 'mods'
        return None

    def check_server_running(self, server_version):
        try:
            server_name, version = server_version.rsplit('_', 1)
        except ValueError:
            return False
        
        with open('assets/servers.json') as f:
            servers = json.load(f)['servers']
        
        for s in servers:
            path = Path(s['path'])
            folder = path.parent.name
            if f"{server_name}_{version}" in folder:
                server_dir = path.parent.resolve()  # 取得絕對路徑
                check_script = f'''
                $serverPath = "{server_dir}".Replace('\', '\\')
                $processes = Get-WmiObject Win32_Process -Filter "name = 'java.exe'"
                foreach ($proc in $processes) {{
                    try {{
                        $procPath = $proc.ExecutablePath
                        if ($procPath -like "*$serverPath*") {{
                            exit 1
                        }}
                    }} catch {{}}
                }}
                exit 0
                '''
                result = subprocess.run(
                    ['powershell', '-Command', check_script],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 1
        return False

    @commands.group(name='mod')
    @commands.has_role('canOpenServer')
    async def mod(self, ctx):
        """模組管理指令群組"""
        if ctx.invoked_subcommand is None:
            await ctx.send('❌ 請指定子指令 (add/disabled/enable/list)')

    @mod.command()
    async def add(self, ctx, server_version: str, url: str):
        """新增模組"""
        mods_dir = self.get_server_path(server_version)
        if not mods_dir:
            return await ctx.send('❌ 找不到伺服器或格式錯誤')
        
        try:
            ps_script = f'''
            $path = "{mods_dir}"
            if (-not (Test-Path $path)) {{ New-Item -ItemType Directory -Path $path }}
            Invoke-WebRequest -Uri "{url}" -OutFile "$path\\{url.split('/')[-1]}"
            '''
            result = subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
            
            if result.returncode != 0:
                raise Exception(result.stderr.decode('big5'))
                
            await ctx.send(f'✅ 已下載模組到 {mods_dir}')
            
        except Exception as e:
            logger.error(f"下載模組失敗: {e}")
            await ctx.send(f'❌ 下載失敗: {str(e)}')

    @mod.command()
    async def disabled(self, ctx, server_version: str, mod_name: str):
        """停用模組"""
        await self.toggle_mod(ctx, server_version, mod_name, disable=True)

    @mod.command()
    async def enable(self, ctx, server_version: str, mod_name: str):
        """啟用模組"""
        await self.toggle_mod(ctx, server_version, mod_name, disable=False)

    async def toggle_mod(self, ctx, server_version, mod_name, disable):
        mods_dir = self.get_server_path(server_version)
        if not mods_dir:
            return await ctx.send('❌ 找不到伺服器')
        
        try:
            mod_file = next((f for f in mods_dir.iterdir() if mod_name in f.name), None)
            if not mod_file:
                raise FileNotFoundError

            new_ext = '.disabled' if disable else '.jar'
            new_name = mod_file.with_suffix(new_ext)
            mod_file.rename(new_name)
            
            action = '停用' if disable else '啟用'
            await ctx.send(f'✅ 已{action} {mod_file.name}')
            
        except Exception as e:
            logger.error(f"切換模組狀態失敗: {e}")
            await ctx.send(f'❌ 操作失敗: {str(e)}')

    @mod.group(name='list', invoke_without_command=True)
    async def mod_list(self, ctx, server_version: str = None):
        """顯示模組清單"""
        if not server_version:
            return await ctx.send('❌ 請指定伺服器_版本')
        
        mods_dir = self.get_server_path(server_version)
        if not mods_dir:
            return await ctx.send('❌ 找不到伺服器')
        
        list_file = mods_dir / 'mod_list.txt'
        if not list_file.exists():
            await ctx.invoke(self.update, server_version)
            
        with open(list_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        await ctx.send(f'📜 模組清單：\n```\n{content[:1900]}\n```')

    @mod_list.command()
    async def update(self, ctx, server_version: str):
        """更新模組清單"""
        if '_' not in server_version:
            return await ctx.send('❌ 格式錯誤，請使用 <伺服器_版本> 格式')
        
        if self.check_server_running(server_version):
            await self.send_desktop_notification(
                "伺服器狀態警告",
                f"{server_version} 正在運行中，操作已阻止"
            )
            return await ctx.send('❌ 伺服器運行中，請先關閉伺服器再操作')
        
        mods_dir = self.get_server_path(server_version)
        if not mods_dir:
            return await ctx.send('❌ 找不到伺服器')
        
        try:
            mod_list = []
            for mod_file in mods_dir.glob('*.*'):
                if mod_file.suffix in ('.jar', '.disabled'):
                    mod_id = '未知'
                    try:
                        # 使用雙重 with 確保資源釋放
                        with zipfile.ZipFile(mod_file, 'r') as z:
                            # 檢查是否為有效 zip 檔案
                            if z.testzip() is not None:
                                raise zipfile.BadZipFile(f"{mod_file.name} 損壞")
                                
                            # 明確指定模式與編碼
                            with z.open('fabric.mod.json', 'r') as f:
                                try:
                                    mod_info = json.load(f)
                                    mod_id = mod_info.get('id', '未知')
                                except json.JSONDecodeError:
                                    logger.warning(f"JSON 解析失敗: {mod_file.name}")
                                    mod_id = 'JSON 解析失敗'
                    except zipfile.BadZipFile as e:
                        logger.warning(f"ZIP 檔案損壞: {mod_file.name} - {str(e)}")
                        mod_id = 'ZIP 損壞'
                    except KeyError:
                        logger.warning(f"找不到 fabric.mod.json: {mod_file.name}")
                        mod_id = '缺少模組資訊'
                    except Exception as e:
                        logger.error(f"解析 {mod_file.name} 發生未預期錯誤: {str(e)}")
                        mod_id = '解析錯誤'
                    
                    mod_list.append(f"{mod_id} | {mod_file.name}")

            list_file = mods_dir / 'mod_list.txt'
            with open(list_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(mod_list))
                
            await ctx.send(f'✅ 已更新模組清單 ({len(mod_list)} 個模組)')
            
        except Exception as e:
            logger.error(f"更新清單失敗: {e}", exc_info=True)
            await ctx.send(f'❌ 更新失敗: {str(e)}')

    async def send_desktop_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Minecraft 伺服器管理',
                timeout=5
            )
        except Exception as e:
            logger.error(f"桌面通知失敗: {e}")

async def setup(bot):
    await bot.add_cog(ModCommands(bot))
    logger.info('Mod 指令已載入') 