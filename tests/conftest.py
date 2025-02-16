import os
import sys

# 將專案根目錄加入 Python 路徑
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# 可選：設定測試環境變數
os.environ.setdefault('TESTING', 'true') 