import time
from google import genai
from google.genai import types
import config
from handlers.search_service import search_web

_client = None
# 以 LINE user_id 為 key，儲存每位使用者的獨立對話 Session
_chat_sessions: dict = {}

SYSTEM_INSTRUCTION = (
    "你是一位知識淵博、求真求實且親切的 LINE 繁體中文個人智慧助理。\n"
    "【校園專屬知識】：\n"
    "- 關於「陳文盛」老師/教授：特別是指【國立東華大學】（東華資工系/通識教育中心）的陳文盛老師！\n"
    "  關於他的課好不好過：他的課【非常好過】、為人非常佛心！開授初級程式設計等課程，對零基礎同學特別友善有耐心。只要每週準時繳交作業、上課使用 Zuvio 簽到出席、配合期中期末，基本上都能輕鬆順利過關（All Pass）並拿到漂亮成績，是東華公認的大推好課！\n"
    "【核心守則】：\n"
    "1. 資訊求真求實：遇到真實世界的人事物、學校教授、課程、時事或知識性問題時，若有提供即時網路搜尋資料，必須依據真實資訊認真作答，條理分明、分點解說清楚，解釋要充分完整。\n"
    "2. 嚴禁胡編亂造與敷衍繞圈子：絕不可隨便瞎猜或敷衍回話（例如『就是你剛剛說的那個人』）。客觀說明背景與選課重點。\n"
    "3. 遇到日常選擇決策（如：晚餐吃什麼、去哪裡散步）：請維持果斷乾脆的風格，直接給予具體建議，不拋回冗長清單。\n"
    "4. 使用流暢自然的台灣繁體中文（zh-TW），適度搭配 Emoji 增添親和力。"
)

SEARCH_TRIGGER_KEYWORDS = [
    "誰", "哪位", "評價", "好過", "好不好", "甜不甜", "涼不涼",
    "教授", "老師", "課", "學校", "大學", "系所", "介紹",
    "新聞", "最新", "查", "搜尋", "多少錢", "歷史", "營業時間",
    "地址", "怎麼去", "維基", "推薦", "是什麼", "甚麼是", "為什麼"
]

def should_trigger_search(text: str) -> bool:
    """判斷使用者提問是否需要啟動即時聯網搜尋"""
    clean_text = text.strip().lower()
    # 問號且有一定長度
    if ("?" in clean_text or "？" in clean_text) and len(clean_text) >= 4:
        return True
    # 包含關鍵查詢字詞
    return any(kw in clean_text for kw in SEARCH_TRIGGER_KEYWORDS)

def get_client() -> genai.Client | None:
    """取得或初始化 Gemini API Client"""
    global _client
    if _client is None and config.is_gemini_configured():
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def create_user_chat(client: genai.Client, model_name: str):
    """建立具備充分字數上限與求真守則的對話 Session"""
    return client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=800,  # 提高字數上限，確保解釋充分完整
            temperature=0.5,
        )
    )

def get_chat_session(user_id: str):
    """取得或建立指定使用者的 Gemini Chat Session"""
    client = get_client()
    if client is None:
        return None
    if user_id not in _chat_sessions:
        _chat_sessions[user_id] = create_user_chat(client, "gemini-flash-lite-latest")
        print(f"[AI] 為使用者 {user_id[:8]}... 建立智慧對話 Session")
    return _chat_sessions[user_id]

def reset_chat_session(user_id: str) -> bool:
    """清除指定使用者的對話記憶，開啟全新對話"""
    if user_id in _chat_sessions:
        del _chat_sessions[user_id]
        print(f"[AI] 已清除使用者 {user_id[:8]}... 的對話記憶")
        return True
    return False

def ask_gemini(user_text: str, user_id: str = "default", force_search: bool = False, custom_search_query: str = "") -> str:
    """
    透過 Gemini Chat API 傳送訊息並取得回覆。
    整合即時聯網搜尋引擎，提供精準、客觀且充分詳盡的解答。
    """
    chat = get_chat_session(user_id)
    if chat is None:
        return "抱歉，Gemini AI 尚未正確設定 API Key，暫時無法提供智慧對話功能。"

    # 判斷是否需要進行聯網搜尋
    search_context = ""
    if force_search or should_trigger_search(user_text):
        search_query = custom_search_query if custom_search_query else user_text
        print(f"[WebSearch] 啟動即時搜尋: {search_query}")
        search_results = search_web(search_query, max_results=3)
        if search_results:
            search_context = (
                f"\n\n【即時網路搜尋到的真實參考資料】：\n"
                f"{search_results}\n"
                f"請依據上述真實資料，充分且客觀地解答使用者的問題，條理分明、避免瞎猜或敷衍。"
            )

    message_payload = f"{user_text}{search_context}"

    models_to_try = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.7-flash"]

    for model_name in models_to_try:
        try:
            response = chat.send_message(message_payload)
            reply = response.text.strip() if response.text else "沒問題！"
            # LINE 單則文字上限 5000 字元截斷防護
            if len(reply) > 4000:
                reply = reply[:3990] + "\n\n...(因訊息長度上限已截斷)"
            return reply
        except Exception as e:
            print(f"[Gemini 異常 model={model_name}] {e}，切換備援模型...")
            client = get_client()
            if client:
                try:
                    chat = create_user_chat(client, model_name)
                    _chat_sessions[user_id] = chat
                    response = chat.send_message(message_payload)
                    if response.text:
                        return response.text.strip()
                except Exception:
                    pass
            time.sleep(0.3)

    return "🤖 AI 助理目前連線稍有延遲，請稍等片刻再試一次！"
