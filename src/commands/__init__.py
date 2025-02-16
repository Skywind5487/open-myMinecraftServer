# 指令模組套件初始化檔案
# 此檔案用於標記 commands 目錄為 Python 子套件
# 版本：1.0.0
# 最後更新：2024-03-29 
import importlib
from pathlib import Path

# 自動偵測 commands 目錄下的模組
command_dir = Path(__file__).parent
__all__ = [
    f.stem for f in command_dir.glob("*.py")
    if f.is_file() and not f.name.startswith('_')
]

# 動態導入所有模組 (可選)
for module in __all__:
    importlib.import_module(f".{module}", __name__) 