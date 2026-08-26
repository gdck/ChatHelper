import os
import sys
import json
import ctypes

# 确保项目根目录在 sys.path 中
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import webview
from src.storage import JsonStorageManager
from src.send_engine import SendEngine
from src.docking_engine import DockingEngine
from src.api import JsApi
from src.tray_manager import TrayManager

def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径（兼容源码运行与 PyInstaller 打包环境）"""
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base, relative_path))

def create_app():
    # 互斥体防多开
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "ChatHelper_Python_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(0, "聊天助手已经在运行中！", "提示", 0x40)
        sys.exit(0)

    # 存储管理器：%APPDATA%\ChatHelper\data.json
    storage = JsonStorageManager()

    send = SendEngine()
    dock = DockingEngine(sidebar_width=480)
    api = JsApi(storage, dock, send)

    # 前端资源路径探测
    html_path = get_resource_path(os.path.join("frontend", "dist", "index.html"))
    if os.path.exists(html_path):
        url = html_path
    else:
        url = "http://localhost:5173"

    window = webview.create_window(
        title="聊天助手",
        url=url,
        js_api=api,
        width=480,
        height=700,
        min_size=(28, 28),
        frameless=True,
        easy_drag=False,
        on_top=True
    )
    api.set_window(window)

    def toggle_helper(icon=None, item=None):
        api.toggleCollapse()

    def exit_app(icon=None, item=None):
        if tray:
            tray.stop()
        dock.stop()
        if window:
            window.destroy()
        os._exit(0)

    tray = TrayManager(on_toggle=toggle_helper, on_exit=exit_app)
    tray.start()

    def on_target_title(title: str):
        try:
            escaped_title = json.dumps(title or "")
            window.evaluate_js(f"window.dispatchEvent(new CustomEvent('target-changed', {{ detail: {escaped_title} }}))")
        except Exception:
            pass

    dock.on_target_changed = on_target_title

    def on_loaded():
        hwnd = ctypes.windll.user32.FindWindowW(None, "聊天助手")
        if hwnd:
            # 纯 POPUP 与 TOOLWINDOW 扩展样式，解除 Windows 窗口最小尺寸限制
            WS_POPUP = 0x80000000
            WS_VISIBLE = 0x10000000
            WS_CLIPCHILDREN = 0x02000000
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_TOPMOST = 0x00000008

            ctypes.windll.user32.SetWindowLongW(hwnd, -16, WS_POPUP | WS_VISIBLE | WS_CLIPCHILDREN)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
            
            # 初始置于屏幕外隐藏，消除闪烁
            ctypes.windll.user32.SetWindowPos(hwnd, 0, -10000, -10000, 10, 10, 0x0010 | 0x0004)
            dock.set_helper_hwnd(hwnd)
            dock.start()
            
            # 启动时智能逻辑：优先激活已运行的 IM 聊天窗口并吸附贴靠；若无则静默驻留托盘
            dock.activate_target_or_hide()

    def on_closing():
        tray.stop()
        dock.stop()

    window.events.loaded += on_loaded
    window.events.closing += on_closing

    webview.start(debug=False)

if __name__ == "__main__":
    create_app()
