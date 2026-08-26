import pytest
import time
from unittest.mock import MagicMock
from src.api import JsApi

def test_api_categories_and_replies():
    mock_db = MagicMock()
    mock_db.get_categories.return_value = [{"id": 1, "name": "售后", "reply_count": 0}]
    mock_db.get_replies.return_value = [{"id": 10, "title": "退货说明", "content": "退货流程...", "attachments": []}]
    mock_dock = MagicMock()
    mock_send = MagicMock()
    
    api = JsApi(mock_db, mock_dock, mock_send)
    
    cats = api.getCategories()
    assert len(cats) == 1
    assert cats[0]["name"] == "售后"

    replies = api.getReplies()
    assert len(replies) == 1
    assert replies[0]["title"] == "退货说明"

def test_api_send_reply():
    mock_db = MagicMock()
    mock_db.get_replies.return_value = [{"id": 10, "title": "退货说明", "content": "退货流程...", "attachments": []}]
    mock_db.get_setting.side_effect = lambda k, d="": d
    mock_dock = MagicMock()
    mock_dock.current_target_hwnd = 12345
    mock_send = MagicMock()
    mock_send.send_payload.return_value = True

    api = JsApi(mock_db, mock_dock, mock_send)
    res = api.sendReply(10, "normal")
    assert res["success"] is True

    # 异步守护线程触发，等待完成
    time.sleep(0.05)
    mock_send.send_payload.assert_called_once_with(
        target_hwnd=12345,
        text="退货流程...",
        attachments=[],
        mode="normal",
        delays={
            "paste_delay": 120,
            "enter_delay": 120,
            "typewriter_delay": 500,
            "repeat_delay": 500
        }
    )
    mock_db.increment_use_count.assert_called_once_with(10)
