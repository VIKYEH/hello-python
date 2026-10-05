import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

def is_gemini_configured():
    """檢查 GEMINI_API_KEY 是否已正確設定"""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")

def validate_config():
    """
    檢查必要環境變數是否已設置。
    若有缺失則回傳缺失的變數名稱列表。
    """
    missing = []
    if not LINE_CHANNEL_SECRET or LINE_CHANNEL_SECRET == "your_channel_secret_here":
        missing.append("LINE_CHANNEL_SECRET")
    if not LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_ACCESS_TOKEN == "your_channel_access_token_here":
        missing.append("LINE_CHANNEL_ACCESS_TOKEN")
    return missing
