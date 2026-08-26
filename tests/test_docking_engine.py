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
    
    wechat_info = TargetWindowInfo(
        hwnd=12345,
        title="文件传输助手",
        class_name="WeChatMainWndForPC",
        process_name="wechat.exe",
        rect=(0, 0, 800, 600)
    )
    assert engine.is_supported_target(wechat_info) is True

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
