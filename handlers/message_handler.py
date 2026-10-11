from datetime import datetime
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent
import config

def generate_reply_text(user_text: str, user_id: str = "default") -> str:
    """
    根據使用者傳入的文字內容，產生對應的回覆文字。
    涵蓋三大情境：
    1. 輸入不完整（純空白字元）：提醒使用者補充文字。
    2. 不支援的輸入（未知指令）：提醒不支援並列出可用指令。
    3. 正常使用（合法指令或 Gemini AI 多輪智慧對話）。
    """
    text = user_text.strip()
    lower_text = text.lower()

    # ── 情境 2：輸入不完整（空白訊息處理） ──────────────────
    if not text:
        return "⚠️ 提示：您輸入的訊息內容是空白的，請輸入想詢問的問題，或輸入 /help 查看指令清單喔！😊"

    # ── 情境 1 & 3：指令處理與不支援指令防護 ────────────────
    if text.startswith("/"):
        if lower_text == "/help":
            ai_status = "✅ 已啟用（支援多輪對話記憶）" if config.is_gemini_configured() else "❌ 未設定 API Key"
            return (
                "🤖 **LINE 智慧助理指令列表**\n"
                "────────────────────\n"
                "• `/help`：查看指令說明\n"
                "• `/time`：查看目前伺服器時間\n"
                "• `/ping`：測試機器人連線狀態\n"
                "• `/reset`：清除對話記憶，重新開始 🔄\n"
                "• 傳送任何其他文字：由 Google Gemini AI 智慧回覆 ✨\n"
                "────────────────────\n"
                f"🧠 Gemini AI 狀態：{ai_status}"
            )
        elif lower_text == "/time":
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"🕒 目前伺服器時間：{now_str}"
        elif lower_text == "/ping":
            return "🏓 Pong！LINE Bot 運作正常。"
        elif lower_text == "/reset":
            if config.is_gemini_configured():
                from handlers.ai_service import reset_chat_session
                reset_chat_session(user_id)
            return "🔄 對話記憶已清除！我們重新開始吧，有什麼想聊的嗎？😊"
        else:
            # 不支援的指令提示
            return (
                f"⚠️ 不支援的指令：`{text}`\n"
                "────────────────────\n"
                "目前支援的指令有：\n"
                "• `/help`：查看功能選單\n"
                "• `/time`：查詢伺服器時間\n"
                "• `/ping`：測試連線狀態\n"
                "• `/reset`：清除對話記憶\n"
                "💡 若想與 Gemini AI 聊天，直接輸入一般文字即可！"
            )

    # ── 情境 1：正常使用（Gemini AI 多輪智慧對話） ───────────
    if config.is_gemini_configured():
        from handlers.ai_service import ask_gemini
        return ask_gemini(text, user_id)
    else:
        return f"你說了：{text}"


def handle_text_message(event: MessageEvent, messaging_api: MessagingApi):
    """
    處理文字訊息事件，並透過 MessagingApi 發送回覆。
    傳入 user_id 以支援多輪對話記憶功能。
    """
    user_text = event.message.text
    reply_token = event.reply_token
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else "default"

    reply_content = generate_reply_text(user_text, user_id)

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=reply_content)]
        )
    )
