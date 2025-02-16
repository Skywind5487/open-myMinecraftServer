#!/usr/bin/env python
import os
import sys
import asyncio

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bot import main

if __name__ == "__main__":
    asyncio.run(main()) 