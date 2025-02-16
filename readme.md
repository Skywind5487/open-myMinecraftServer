# 🎮 Minecraft 伺服器管理機器人
![Wiki](https://github.com/Skywind5487/open-myMinecraftServer/blob/main/assets/wiki)

🤖 專為 Minecraft 伺服器打造的 Discord 整合管理解決方案

## ✨ 主要功能

### 🚀 核心控制
- 一鍵式伺服器啟動

### 🌐 雲端整合
- Alist 雲端存檔管理(不會幫你建好，需要自己建)

### 📊 資訊顯示
- 即時伺服器列表
- 網路延遲檢測
- 版本核心監控
- 連線端口管理

## 🛠️ 快速開始

### 前置需求
- Python 3.10+
- Poetry 依賴管理
- Discord 機器人 Token

### 安裝步驟
```bash
# 複製儲存庫
git clone https://github.com/Skywind5487/open-myMinecraftServer.git

# 安裝依賴
poetry install

# 設定環境變數 
cp .env.example .env
```

### 啟動機器人
```bash
poetry run python script/run.py
```

## 📌 使用提示
```bash
# 開發模式 (含熱重載)
poetry run dev

# 執行測試
poetry run pytest tests/
```



> 💡 需要完整文件或客製化部署？請聯繫專案維護者！


