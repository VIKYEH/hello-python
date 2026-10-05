from datetime import datetime
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent
import config

def generate_reply_text(user_text: str) -> str:
    """
    根據使用者傳入的文字內容，產生對應的回覆文字。
    - 內建指令（/help、/time、/ping）直接回覆，不消耗 AI 額度。
    - 一般訊息則交由 Gemini AI 智慧回覆。
    """
    text = user_text.strip()
    lower_text = text.lower()

    # ── 內建指令（不呼叫 AI） ──────────────────────────
    if lower_text == "/help":
        ai_status = "✅ 已啟用" if config.is_gemini_configured() else "❌ 未設定 API Key"
        return (
            "🤖 **LINE 智慧助理指令列表**\n"
            "────────────────────\n"
            "• `/help`：查看指令說明\n"
            "• `/time`：查看目前伺服器時間\n"
            "• `/ping`：測試機器人連線狀態\n"
            "• 傳送任何其他文字：由 Google Gemini AI 智慧回覆 ✨\n"
            "────────────────────\n"
            f"🧠 Gemini AI 狀態：{ai_status}"
        )
    elif lower_text == "/time":
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"🕒 目前伺服器時間：{now_str}"
    elif lower_text == "/ping":
        return "🏓 Pong！LINE Bot 運作正常。"

    # ── Gemini AI 智慧回覆 ────────────────────────────
    if config.is_gemini_configured():
        from handlers.ai_service import ask_gemini
        return ask_gemini(text)
    else:
        # AI 未設定時，保留原本的回音模式作為備用
        return f"你說了：{text}"


def handle_text_message(event: MessageEvent, messaging_api: MessagingApi):
    """
    處理文字訊息事件，並透過 MessagingApi 發送回覆。
    """
    user_text = event.message.text
    reply_token = event.reply_token

    reply_content = generate_reply_text(user_text)

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=reply_content)]
        )
    )
