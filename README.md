# 🤖 Python LINE Bot 專案 (LINE Messaging API v3)

本專案採用官方最新版 **LINE Messaging API SDK v3**（`line-bot-sdk>=3.14.0`）與 **Flask** 網頁框架建置，具備數位簽章安全驗證、環境變數機密保護、模組化訊息路由與自動化測試套件。

---

## 📁 專案檔案結構

```text
hello-python/
├── .env                  # 本機環境變數（包含 LINE 金鑰，已被 .gitignore 排除）
├── .env.example          # 環境變數範本檔
├── .gitignore            # Git 忽略設定，防止金鑰外流
├── app.py                # 主伺服器程式（Webhook 接收、簽章檢驗與健康檢查）
├── config.py             # 設定載入與環境變數檢查模組
├── requirements.txt      # 專案相依套件清單
├── README.md             # 專案說明與操作文件
├── handlers/             # 訊息與事件處理邏輯模組
│   ├── __init__.py
│   └── message_handler.py# 訊息路由與指令回覆邏輯
└── tests/                # 自動化測試模組
    ├── __init__.py
    └── test_webhook.py   # 端點健康與簽章防護單元測試
```

---

## 🛠️ 快速開始

### 1. 安裝套件依賴
確認已安裝 Python 3.10+，於終端機執行：
```powershell
pip install -r requirements.txt
```

### 2. 設定環境變數
將 `.env.example` 複製一份為 `.env`（專案內已為您預先建立）：
```powershell
copy .env.example .env
```
打開 `.env` 檔案並填入您的 LINE 金鑰：
```env
LINE_CHANNEL_SECRET=你的_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
PORT=5000
DEBUG=True
```

---

## 📱 LINE Developers 後台申請與設定指南

若要讓機器人在 LINE 上正常收發訊息，請按照以下步驟完成設定：

### 步驟 A：建立 Messaging API Channel
1. 前往 [LINE Developers Console](https://developers.line.biz/) 並登入您的 LINE 帳號。
2. 建立或選擇一個 **Provider**（提供者）。
3. 點選 **Create a new channel**，選擇 **Messaging API**。
4. 填寫機器人基本資訊（名稱、說明、類別、電子信箱等），點擊建立。

### 步驟 B：取得金鑰資訊
1. **取得 Channel Secret**：
   - 進入建立好的 Channel 頁面，點選 **Basic settings** 分頁。
   - 找到 **Channel secret**，複製並填入 `.env` 檔案中的 `LINE_CHANNEL_SECRET`。
2. **取得 Channel Access Token**：
   - 切換至 **Messaging API** 分頁。
   - 滾動至最下方的 **Channel access token**。
   - 點擊 **Issue** 按鈕生成長效 Token，複製並填入 `.env` 檔案中的 `LINE_CHANNEL_ACCESS_TOKEN`。

### 步驟 C：調整 LINE 官方回應設定（重要）
1. 在 **Messaging API** 分頁中，找到 **LINE Official Account features**。
2. 點選 **Auto-reply messages** 旁的 **Edit**。
3. 在跳出的設定頁面中：
   - 將 **聊天 (Chat)** 設為開啟或關閉皆可。
   - 將 **自動回應訊息 (Auto-response messages)** 設為 **停用 (Disabled)**（*避免 LINE 官方系統與您的機器人同時回覆造成雙重回話*）。
   - 將 **Webhook** 設為 **啟用 (Enabled)**。

---

## 🌐 本地測試與 ngrok 外網穿透

因為 LINE 伺服器必須透過公開的 **HTTPS 網址** 發送 Webhook 請求，本地開發建議使用 `ngrok`：

1. **啟動本機 LINE Bot 伺服器**：
   ```powershell
   python app.py
   ```
   伺服器預設會於 `http://127.0.0.1:5000` 啟動。

2. **啟動 ngrok 建立 HTTPS 通道**（另開一個終端機視窗）：
   ```powershell
   ngrok http 5000
   ```
   ngrok 會顯示轉發網址，例如：`https://xxxx-xx-xx.ngrok-free.app`

3. **設定 LINE Webhook URL**：
   - 回到 LINE Developers 的 **Messaging API** 分頁。
   - 找到 **Webhook settings**，在 **Webhook URL** 欄位填入：
     `https://xxxx-xx-xx.ngrok-free.app/callback`
   - 點擊 **Update** 儲存。
   - 點擊 **Verify** 按鈕測試連線，若回傳 `Success` 代表連線成功！
   - 確認 **Use webhook** 開關已切換為 **開啟 (Enabled)**。

4. **加入好友並開始聊天**：
   - 在 Messaging API 頁面掃描 QR Code 將機器人加入好友。
   - 發送訊息即可進行測試！

---

## 💡 內建指令與功能說明

| 指令 | 說明 |
| :--- | :--- |
| `/help` | 查看機器人說明選單與可用指令 |
| `/time` | 查詢伺服器目前的日期與時間 |
| `/ping` | 測試機器人連線狀態（回應 Pong） |
| *任意其他文字* | 機器人將自動進行回音（Echo） |

---

## 🧪 執行自動化測試

本專案包含完整的單元測試套件，執行以下指令即可檢驗伺服器健康檢查與簽章防護機制：
```powershell
pytest tests/ -v
```
