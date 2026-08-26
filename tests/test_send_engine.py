import datetime
import pytest
from src.send_engine import SendEngine
from src.win32_clipboard import Win32Clipboard
import tempfile
import os

def test_variable_interpolation():
    engine = SendEngine()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    template = "尊敬的客户您好，今天是{日期}，请查收！"
    result = engine.interpolate_variables(template)
    assert today_str in result
    assert "{日期}" not in result

def test_greeting_interpolation():
    engine = SendEngine()
    result = engine.interpolate_variables("祝您{问候语}，合作愉快！")
    assert any(g in result for g in ["早上好", "上午好", "中午好", "下午好", "晚上好"])

def test_custom_variables():
    engine = SendEngine()
    template = "你好 {客户名}，您的订单号为 {订单号}"
    result = engine.interpolate_variables(template, {"客户名": "张总", "订单号": "WX123456"})
    assert result == "你好 张总，您的订单号为 WX123456"

def test_win32_clipboard_text():
    # 测试剪贴板文本设置
    success = Win32Clipboard.set_text("测试剪贴板文本写入 123456 ABC")
    assert success is True

def test_win32_clipboard_files():
    # 创建临时文件测试 CF_HDROP
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test file content")
        temp_path = f.name
    try:
        success = Win32Clipboard.set_files([temp_path])
        assert success is True
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
