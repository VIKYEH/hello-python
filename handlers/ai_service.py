import os
import time
from google import genai
from google.genai import types
import config

_client = None

def get_client() -> genai.Client | None:
    """取得或初始化 Gemini API Client"""
    global _client
    if _client is None and config.is_gemini_configured():
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def ask_gemini(prompt: str) -> str:
    """
    呼叫 Google Gemini 模型產生繁體中文智慧回覆。
    支援模型降級備援機制（gemini-3.7-flash -> gemini-3.5-flash -> gemini-3.8-flash）。
    """
    client = get_client()
    if not client:
        return "抱歉，Gemini AI 尚未正確設定 API Key，暫時無法提供智慧對話功能。"

    system_instruction = (
        "你是一位親切、幽默且知識淵博的 LINE 繁體中文智慧助理。"
        "請使用流暢自然、符合台灣用語習慣的繁體中文（zh-TW）回答。"
        "回答要清晰簡潔、有條理，並適度使用 Emoji 表情符號增添趣味。"
    )

    models_to_try = ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.8-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=1500,
                    temperature=0.7,
                )
            )
            reply = response.text.strip() if response.text else "抱歉，我暫時想不到該如何回應這則訊息。"
            # LINE 單則文字上限為 5000 字元
            if len(reply) > 4000:
                reply = reply[:3990] + "\n\n...(因 LINE 訊息字數上限已截斷)"
            return reply
        except Exception as e:
            print(f"[Gemini 呼叫異常 model={model_name}] {e}")
            time.sleep(0.5)

    return "🤖 AI 助理正在忙碌中或連線稍有延遲，請稍等片刻再試一次！"
