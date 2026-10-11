import pytest
from app import app
from handlers.message_handler import generate_reply_text

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check_endpoint(client):
    """測試健康檢查端點正常回應"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert data["service"] == "line-bot-server"
    assert "message" in data

def test_callback_without_signature_rejected(client):
    """缺少簽章時應回傳 400 錯誤"""
    response = client.post("/callback", data="test_payload")
    assert response.status_code == 400

def test_callback_invalid_signature_rejected(client):
    """提供無效或偽造簽章時應回傳 400 錯誤"""
    headers = {"X-Line-Signature": "invalid_fake_signature"}
    response = client.post("/callback", headers=headers, data="test_payload")
    assert response.status_code == 400

def test_scenario_1_normal_usage():
    """【情境 1：正常使用測試】主要功能與指令是否正常完成？"""
    # 測試 /help 指令
    help_reply = generate_reply_text("/help", "user_1")
    assert "指令" in help_reply
    assert "/time" in help_reply
    assert "/reset" in help_reply

    # 測試 /time 指令
    time_reply = generate_reply_text("/time", "user_1")
    assert "目前伺服器時間" in time_reply

    # 測試 /ping 指令
    ping_reply = generate_reply_text("/ping", "user_1")
    assert "Pong" in ping_reply

    # 測試 /reset 重設記憶指令
    reset_reply = generate_reply_text("/reset", "user_1")
    assert "對話記憶已清除" in reset_reply

def test_scenario_2_incomplete_input():
    """【情境 2：輸入不完整測試】輸入空白或無內容時，是否提醒使用者補充？"""
    reply_empty = generate_reply_text("", "user_1")
    assert "空白" in reply_empty or "提示" in reply_empty

    reply_spaces = generate_reply_text("    ", "user_1")
    assert "空白" in reply_spaces or "提示" in reply_spaces

def test_scenario_3_unsupported_input():
    """【情境 3：不支援的輸入測試】輸入未定義的指令時，是否提供使用提示？"""
    reply_invalid = generate_reply_text("/unknown_command", "user_1")
    assert "不支援的指令" in reply_invalid
    assert "/help" in reply_invalid
    assert "目前支援的指令有" in reply_invalid
