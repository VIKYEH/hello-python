import sys
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import config
from handlers.message_handler import handle_text_message

# 設定 Windows 終端機 UTF-8 編碼
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)

# LINE Bot SDK v3 設定
configuration = Configuration(access_token=config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def health_check():
    """
    伺服器健康檢查端點。
    可由瀏覽器或外部監控工具檢查伺服器是否就緒。
    """
    missing_keys = config.validate_config()
    is_ready = len(missing_keys) == 0
    return jsonify({
        "status": "ready" if is_ready else "unconfigured",
        "service": "line-bot-server",
        "missing_config": missing_keys,
        "message": "LINE Bot 伺服器運作中！" if is_ready else "請在 .env 檔案中設定 LINE 金鑰以啟用完整功能。"
    }), 200

@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE Webhook 回呼入口點。
    驗證 X-Line-Signature 數位簽章後交給 handler 處理。
    """
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    if not signature:
        app.logger.warning("收到未包含 X-Line-Signature 的請求。")
        abort(400)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("無效的數位簽章 (InvalidSignatureError)。")
        abort(400)
    except Exception as e:
        app.logger.error(f"處理 Webhook 時發生未預期錯誤: {e}")
        abort(500)

    return "OK", 200

@handler.add(MessageEvent, message=TextMessageContent)
def on_message_event(event):
    """
    監聽文字訊息事件並轉發給處理模組。
    """
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        handle_text_message(event, messaging_api)

if __name__ == "__main__":
    missing = config.validate_config()
    if missing:
        print(f"[提示] 目前尚未設定以下環境變數: {', '.join(missing)}")
        print("您可以在 .env 檔案中填寫 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN。")
    print(f"啟動伺服器於 http://127.0.0.1:{config.PORT} ...")
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
