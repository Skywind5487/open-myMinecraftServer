import subprocess
import psutil
import os
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

class MinecraftServer:
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.process: Optional[subprocess.Popen] = None
        self.pid_file = os.path.join(server_path, "server.pid")
        self.bat_file = os.path.join(server_path, "start.bat")

    async def start(self) -> bool:
        if self.is_running():
            logger.warning("伺服器已經在運行中")
            return False

        try:
            # 啟動伺服器
            self.process = subprocess.Popen(
                self.bat_file,
                cwd=self.server_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # 儲存 PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.process.pid))
            
            logger.info(f"伺服器已啟動，PID: {self.process.pid}")
            return True

        except Exception as e:
            logger.error(f"啟動伺服器時發生錯誤: {e}")
            return False

    async def stop(self) -> bool:
        if not self.is_running():
            logger.warning("伺服器未運行")
            return False

        try:
            pid = self.get_server_pid()
            if pid:
                process = psutil.Process(pid)
                process.terminate()
                
                # 等待程序結束
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    process.kill()  # 強制結束
                
                # 清除 PID 文件
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
                
                logger.info("伺服器已停止")
                return True

        except Exception as e:
            logger.error(f"停止伺服器時發生錯誤: {e}")
            return False

    def is_running(self) -> bool:
        pid = self.get_server_pid()
        if pid is None:
            return False
        
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

    def get_server_pid(self) -> Optional[int]:
        if not os.path.exists(self.pid_file):
            return None
            
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except:
            return None

    async def get_status(self) -> dict:
        if not self.is_running():
            return {"status": "offline", "memory_usage": 0, "cpu_usage": 0}
        
        pid = self.get_server_pid()
        try:
            process = psutil.Process(pid)
            return {
                "status": "online",
                "memory_usage": process.memory_percent(),
                "cpu_usage": process.cpu_percent(),
                "pid": pid
            }
        except:
            return {"status": "error", "memory_usage": 0, "cpu_usage": 0}
