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
    1. 輸入不完整（純空白字元或指令缺參數）：提醒使用者補充文字。
    2. 不支援的輸入（未知指令）：提醒不支援並列出可用指令。
    3. 正常使用（合法指令或 Gemini AI 智慧聯網對話）。
    """
    text = user_text.strip()
    lower_text = text.lower()

    # ── 情境 2：輸入不完整（空白訊息處理） ──────────────────
    if not text:
        return "⚠️ 提示：您輸入的訊息內容是空白的，請輸入想詢問的問題，或輸入 /help 查看指令清單喔！😊"

    # ── 指令處理與不支援指令防護 ────────────────────────────
    if text.startswith("/"):
        # 1. /help 說明
        if lower_text == "/help":
            ai_status = "✅ 已啟用（支援即時聯網搜尋與多輪記憶）" if config.is_gemini_configured() else "❌ 未設定 API Key"
            return (
                "🤖 **LINE 智慧助理指令列表**\n"
                "────────────────────\n"
                "• `/help`：查看指令說明\n"
                "• `/search <關鍵字>`：即時聯網深度搜尋 🔍\n"
                "• `/查 <關鍵字>`：搜尋快捷鍵\n"
                "• `/time`：查看目前伺服器時間\n"
                "• `/ping`：測試機器人連線狀態\n"
                "• `/reset`：清除對話記憶，重新開始 🔄\n"
                "• 直接傳送任何文字：AI 自動判斷並連網查證作答 ✨\n"
                "────────────────────\n"
                f"🧠 Gemini AI 狀態：{ai_status}"
            )

        # 2. /time 時間
        elif lower_text == "/time":
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"🕒 目前伺服器時間：{now_str}"

        # 3. /ping 連線
        elif lower_text == "/ping":
            return "🏓 Pong！LINE Bot 運作正常。"

        # 4. /reset 清除記憶
        elif lower_text == "/reset":
            if config.is_gemini_configured():
                from handlers.ai_service import reset_chat_session
                reset_chat_session(user_id)
            return "🔄 對話記憶已清除！我們重新開始吧，有什麼想聊的嗎？😊"

        # 5. /search 或 /查 手動即時搜尋
        elif lower_text.startswith("/search") or text.startswith("/查"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                return "⚠️ 請在搜尋指令後方加上關鍵字喔！例如：\n• `/search 陳文盛`\n• `/查 陽明交大選課評價`"
            search_keyword = parts[1].strip()
            if config.is_gemini_configured():
                from handlers.ai_service import ask_gemini
                return ask_gemini(
                    user_text=f"請幫我詳細查詢介紹：{search_keyword}",
                    user_id=user_id,
                    force_search=True,
                    custom_search_query=search_keyword
                )
            else:
                return f"🔍 欲搜尋關鍵字：{search_keyword}（AI 尚未設定 API Key）"

        # 6. 不支援的未知指令提示
        else:
            return (
                f"⚠️ 不支援的指令：`{text}`\n"
                "────────────────────\n"
                "目前支援的指令有：\n"
                "• `/help`：查看功能選單\n"
                "• `/search <關鍵字>`：即時聯網搜尋\n"
                "• `/time`：查詢伺服器時間\n"
                "• `/ping`：測試連線狀態\n"
                "• `/reset`：清除對話記憶\n"
                "💡 若想與 Gemini AI 聊天，直接輸入一般文字即可！"
            )

    # ── 情境 1：正常使用（Gemini AI 智慧對話，自動啟動聯網搜尋） ───
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
