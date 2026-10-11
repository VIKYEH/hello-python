# 🤖 Python LINE Bot AI 智慧助理 (LINE Messaging API v3 + Gemini)

本專案採用官方最新版 **LINE Messaging API SDK v3**（`line-bot-sdk>=3.14.0`）、**Flask** 網頁框架以及 **Google GenAI (Gemini)** 建置，並成功部署於 **Render 雲端平台** 達成 24 小時不中斷在線運作。

- 🌐 **開發與改善紀錄網頁（GitHub Pages）**：[https://vikyeh.github.io/hello-python/](https://vikyeh.github.io/hello-python/)
- ☁️ **Render 雲端服務網址**：`https://hello-python-line-bot.onrender.com`
- 📦 **v1.0 第一版 Release 標籤**：[`v1.0` (commit `d2d6c2f`)](https://github.com/VIKYEH/hello-python/tree/v1.0)
- 🚀 **v2.0 改善版本**：新增多輪對話記憶（Multi-turn Chat Memory）與 `/reset` 指令

---

## 📌 版本演進與改善紀錄 (Changelog)

### [v2.0 改善版本] - 2026-10-11
- **原本的問題**：v1.0 採用單次呼叫（無狀態），AI 缺乏上下文記憶，使用者追問「那裡、他、剛剛說的」等代名詞時無法連貫回答。
- **修改內容**：
  - 核心 AI 模組重構：改用 `google-genai` 的 `client.chats.create()`，並以 LINE `user_id` 作為 Key 建立每位使用者的獨立對話 Session。
  - 訊息路由升級：新增 `/reset` 指令供使用者隨時清空記憶重啟話題；更新 `/help` 指令選單顯示狀態。
  - 系統架構升級：新增多模型平滑降級備援（`gemini-3.7-flash` -> `gemini-3.5-flash` -> `gemini-3.8-flash`）。
  - 建立完整開發紀錄網頁於 `docs/index.html`。
- **重新測試結果**：單元測試 4 項全數 PASS，真實 LINE 多輪對話實測記憶連貫正常。

### [v1.0 第一版] - 2026-10-05 (Tag: `v1.0`)
- 基礎架構建置：Flask + LINE SDK v3 數位簽章驗證（`X-Line-Signature`）。
- 基礎系統指令：`/help`、`/time`、`/ping`。
- 整合 Google Gemini 3.7 Flash 智慧問答。
- 成功部署至 Render 免費雲端伺服器，完成 LINE Webhook 連線驗證。

---

## 📁 專案檔案結構

```text
hello-python/
├── .env                  # 本機環境變數（已排除於 Git）
├── .env.example          # 環境變數範本檔
├── .gitignore            # Git 忽略設定
├── Procfile              # Render 雲端啟動設定 (gunicorn)
├── app.py                # 主伺服器程式（Webhook 接收、簽章檢驗與健康檢查）
├── config.py             # 設定載入與環境變數檢查模組
├── requirements.txt      # 專案相依套件清單
├── README.md             # 專案說明與操作文件
├── docs/                 # 開發紀錄網頁 (GitHub Pages)
│   └── index.html        # 完整改善紀錄網頁
├── handlers/             # 處理邏輯模組
│   ├── __init__.py
│   ├── ai_service.py     # Gemini 多輪對話服務模組（支援 session 隔離）
│   └── message_handler.py# 訊息路由與指令回覆邏輯
└── tests/                # 自動化測試模組
    ├── __init__.py
    └── test_webhook.py   # 端點健康與簽章防護單元測試
```

---

## 💡 內建指令與功能說明

| 指令 | 說明 | 處理方式 |
| :--- | :--- | :--- |
| `/help` | 查看機器人說明選單與功能狀態 | 本地秒回（不消耗 AI 額度） |
| `/time` | 查詢伺服器目前的日期與時間 | 本地秒回 |
| `/ping` | 測試機器人連線狀態（回應 Pong） | 本地秒回 |
| `/reset` | **清除對話記憶，重啟新對話** | 清空該用戶之對話 Session |
| *任意其他文字* | **由 Google Gemini AI 進行多輪智慧問答** | 支援前後文上下文理解 |

---

## 🛠️ 本地開發與測試

```powershell
# 1. 安裝套件
pip install -r requirements.txt

# 2. 執行自動化測試
pytest tests/ -v

# 3. 啟動伺服器
python app.py
```
