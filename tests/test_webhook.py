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

def test_message_handler_commands():
    """測試各項指令生成邏輯"""
    # 測試 /help 指令
    help_reply = generate_reply_text("/help")
    assert "指令" in help_reply
    assert "/time" in help_reply

    # 測試 /time 指令
    time_reply = generate_reply_text("/time")
    assert "目前伺服器時間" in time_reply

    # 測試 /ping 指令
    ping_reply = generate_reply_text("/ping")
    assert "Pong" in ping_reply

    # 測試一般回音備用邏輯（Gemini 未設定時）
    import unittest.mock as mock
    import config
    with mock.patch.object(config, 'GEMINI_API_KEY', ''):
        echo_reply = generate_reply_text("你好，這是一則測試訊息")
        assert echo_reply == "你說了：你好，這是一則測試訊息"
