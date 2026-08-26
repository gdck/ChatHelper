import pytest
from src.docking_engine import DockingEngine, TargetWindowInfo

def test_docking_rect_calculations():
    engine = DockingEngine(sidebar_width=408)
    target_rect = (100, 100, 900, 700) # left, top, right, bottom
    
    # 展开模式：吸附在右侧，宽度 408
    expanded_pos = engine.calculate_dock_pos(target_rect, collapsed=False, sidebar_width=408)
    assert expanded_pos == (900, 100, 408, 600)

    # 折叠模式：右上角 28x28 极简微标 (Delphi 原版逻辑)
    collapsed_pos = engine.calculate_dock_pos(target_rect, collapsed=True, icon_size=28)
    assert collapsed_pos == (872, 72, 28, 28)

def test_is_supported_target():
    engine = DockingEngine()
    
    # 传统 WeChat 3.x
    wechat_info = TargetWindowInfo(
        hwnd=12345,
        title="文件传输助手",
        class_name="WeChatMainWndForPC",
        process_name="wechat.exe",
        rect=(0, 0, 800, 600)
    )
    assert engine.is_supported_target(wechat_info) is True

    # 现代化重构版 WeChat 4.0 (Weixin.exe + WeixinMainWndForPC / Chrome_WidgetWin_1)
    modern_weixin_info = TargetWindowInfo(
        hwnd=12346,
        title="微信业务交流群",
        class_name="Chrome_WidgetWin_1",
        process_name="weixin.exe",
        rect=(50, 50, 950, 750)
    )
    assert engine.is_supported_target(modern_weixin_info) is True

    qq_chat_info = TargetWindowInfo(
        hwnd=23456,
        title="技术交流群",
        class_name="TXGuiFoundation",
        process_name="qq.exe",
        rect=(100, 100, 700, 600)
    )
    assert engine.is_supported_target(qq_chat_info) is True

    qq_dialog_info = TargetWindowInfo(
        hwnd=34567,
        title="提示",
        class_name="TXGuiFoundation",
        process_name="qq.exe",
        rect=(200, 200, 500, 360) # 300x160 小弹窗
    )
    assert engine.is_supported_target(qq_dialog_info) is False

    unsupported_info = TargetWindowInfo(
        hwnd=67890,
        title="记事本",
        class_name="Notepad",
        process_name="notepad.exe",
        rect=(0, 0, 800, 600)
    )
    assert engine.is_supported_target(unsupported_info) is False

def test_toggle_collapse():
    engine = DockingEngine()
    assert engine.collapsed is False
    state = engine.toggle_collapse()
    assert state is True
    assert engine.collapsed is True
    state2 = engine.toggle_collapse()
    assert state2 is False
    assert engine.collapsed is False
