import time
from google import genai
from google.genai import types
import config

_client = None
# 以 LINE user_id 為 key，儲存每位使用者的獨立對話 Session
_chat_sessions: dict = {}

SYSTEM_INSTRUCTION = (
    "你是一位親切、幽默且知識淵博的 LINE 繁體中文智慧助理。"
    "請使用流暢自然、符合台灣用語習慣的繁體中文（zh-TW）回答。"
    "回答要清晰簡潔、有條理，並適度使用 Emoji 表情符號增添趣味。"
    "你能記住這段對話中使用者說過的內容，並依據上下文給出連貫的回答。"
)

def get_client() -> genai.Client | None:
    """取得或初始化 Gemini API Client"""
    global _client
    if _client is None and config.is_gemini_configured():
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def get_chat_session(user_id: str):
    """
    取得或建立指定使用者的 Gemini Chat Session。
    每位 LINE 使用者擁有獨立的對話記憶，互不干擾。
    """
    client = get_client()
    if client is None:
        return None
    if user_id not in _chat_sessions:
        _chat_sessions[user_id] = client.chats.create(
            model="gemini-3.7-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=1500,
                temperature=0.7,
            )
        )
        print(f"[AI] 為使用者 {user_id[:8]}... 建立新的對話 Session")
    return _chat_sessions[user_id]

def reset_chat_session(user_id: str) -> bool:
    """清除指定使用者的對話記憶，開啟全新對話"""
    if user_id in _chat_sessions:
        del _chat_sessions[user_id]
        print(f"[AI] 已清除使用者 {user_id[:8]}... 的對話記憶")
        return True
    return False

def ask_gemini(user_text: str, user_id: str = "default") -> str:
    """
    透過 Gemini Chat API 傳送訊息並取得回覆。
    支援多輪對話記憶：同一位使用者的對話歷史會被保留，
    讓 AI 能理解上下文，給出連貫自然的回應。
    """
    chat = get_chat_session(user_id)
    if chat is None:
        return "抱歉，Gemini AI 尚未正確設定 API Key，暫時無法提供智慧對話功能。"

    models_to_try = ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.8-flash"]

    for model_name in models_to_try:
        try:
            # 若 session 使用的 model 需要備援，重建 session 使用新 model
            if chat._model != f"models/{model_name}":
                try:
                    response = chat.send_message(user_text)
                except Exception:
                    # 當前 model 失敗，換備援 model 重建 session
                    client = get_client()
                    new_chat = client.chats.create(
                        model=model_name,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            max_output_tokens=1500,
                            temperature=0.7,
                        )
                    )
                    _chat_sessions[user_id] = new_chat
                    response = new_chat.send_message(user_text)
            else:
                response = chat.send_message(user_text)

            reply = response.text.strip() if response.text else "抱歉，我暫時想不到該如何回應這則訊息。"
            # LINE 單則文字上限 5000 字元，安全截斷
            if len(reply) > 4000:
                reply = reply[:3990] + "\n\n...(因 LINE 訊息字數上限已截斷)"
            return reply

        except Exception as e:
            print(f"[Gemini 呼叫異常 model={model_name}] {e}")
            time.sleep(0.5)

    return "🤖 AI 助理正在忙碌中或連線稍有延遲，請稍等片刻再試一次！"
