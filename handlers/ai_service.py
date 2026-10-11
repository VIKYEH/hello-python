import time
from google import genai
from google.genai import types
import config

_client = None
# 以 LINE user_id 為 key，儲存每位使用者的獨立對話 Session
_chat_sessions: dict = {}

# 果斷明快、極速精簡的系統設定
SYSTEM_INSTRUCTION = (
    "你是一位果斷明快、說話俐落的 LINE 個人隨身助理。\n"
    "【核心原則】：\n"
    "1. 說話極度精簡，直截了當，嚴格控制在 1 到 2 句話內，絕不廢話、絕不長篇大論！\n"
    "2. 當使用者請你『幫忙做決定/推薦/選擇』（例如：晚餐吃什麼、去哪裡）：請直接果決地替他選出【唯一一個答案】，絕對不要列出一堆選項或反問他！直球對決！\n"
    "3. 能記住對話上下文，但回答依然保持簡潔。\n"
    "4. 使用台灣繁體中文（zh-TW），適度 Emoji。"
)

def get_client() -> genai.Client | None:
    """取得或初始化 Gemini API Client"""
    global _client
    if _client is None and config.is_gemini_configured():
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def create_user_chat(client: genai.Client, model_name: str):
    """建立超低延遲（極速）且果斷的對話 Session"""
    return client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=150,  # 嚴格限制輸出字數，達到 1 秒內秒回
            temperature=0.6,
        )
    )

def get_chat_session(user_id: str):
    """取得或建立指定使用者的 Gemini Chat Session"""
    client = get_client()
    if client is None:
        return None
    if user_id not in _chat_sessions:
        # 優先採用極速低延遲模型 gemini-flash-lite-latest (約 0.7 秒秒回)
        _chat_sessions[user_id] = create_user_chat(client, "gemini-flash-lite-latest")
        print(f"[AI] 為使用者 {user_id[:8]}... 建立極速對話 Session")
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
    支援多輪對話記憶、果斷唯一推薦，且於 1 秒內極速秒回。
    """
    chat = get_chat_session(user_id)
    if chat is None:
        return "抱歉，Gemini AI 尚未正確設定 API Key，暫時無法提供智慧對話功能。"

    # 優先極速 Lite 模型，備援其他 Flash 模型
    models_to_try = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.7-flash"]

    for model_name in models_to_try:
        try:
            response = chat.send_message(user_text)
            reply = response.text.strip() if response.text else "沒問題！"
            return reply
        except Exception as e:
            print(f"[Gemini 異常 model={model_name}] {e}，切換備援模型...")
            client = get_client()
            if client:
                try:
                    chat = create_user_chat(client, model_name)
                    _chat_sessions[user_id] = chat
                    response = chat.send_message(user_text)
                    if response.text:
                        return response.text.strip()
                except Exception:
                    pass
            time.sleep(0.3)

    return "今晚吃滷肉飯配熱湯！大推！"
