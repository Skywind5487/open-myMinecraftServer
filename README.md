# Minecraft 伺服器管理系統

## 專案架構
```
OPEN-MYMINECRAFTSERVER
├── config/                 # 設定檔案目錄
│   └── server.json        # 伺服器設定檔
├── src/
│   ├── interface/         # 使用者介面層
│   │   ├── discord/      # Discord Bot 介面
│   │   └── cli/          # 終端機介面
│   ├── service/          # 業務邏輯層
│   └── utils/            # 通用工具
├── main.py               # 主程式入口
├── pyproject.toml        # Poetry 設定
└── .env                  # 環境變數
```

## 功能特色
- 多重介面：支援終端機和 Discord 同時操作
- 伺服器管理：啟動、停止、監控伺服器狀態
- 彈性配置：支援多種伺服器核心和版本

## 快速開始
1. 安裝依賴：
```bash
poetry install
```

2. 設定環境變數：
將 `.env.example` 複製為 `.env` 並填入設定

3. 啟動系統：
```bash
# 完整模式（同時啟動終端機和 Discord）
poetry run start

# 僅終端機模式
poetry run start --terminal

# 僅 Discord 模式
poetry run start --discord
```

## 常用指令
- `list` - 顯示所有伺服器
- `add <path> [-f] [-d "描述"]` - 新增伺服器
- `remove <name_version>` - 移除伺服器
- `help` - 顯示指令說明