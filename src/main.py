import os
import sys
import webview
import ctypes
from src.database import DatabaseManager
from src.send_engine import SendEngine
from src.docking_engine import DockingEngine
from src.api import JsApi

def create_app():
    # 互斥体防多开
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "ChatHelper_Python_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(0, "聊天助手已经在运行中！", "提示", 0x40)
        sys.exit(0)

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chat_helper.db")
    db = DatabaseManager(db_path)
    db.init_db()

    send = SendEngine()
    dock = DockingEngine(sidebar_width=408)
    api = JsApi(db, dock, send)

    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
    if os.path.exists(os.path.join(frontend_dir, "index.html")):
        url = os.path.join(frontend_dir, "index.html")
    else:
        url = "http://localhost:5173"

    window = webview.create_window(
        title="微信聊天助手",
        url=url,
        js_api=api,
        width=408,
        height=700,
        frameless=True,
        easy_drag=False,
        on_top=True
    )
    api.set_window(window)

    def on_target_title(title: str):
        try:
            window.evaluate_js(f"window.dispatchEvent(new CustomEvent('target-changed', {{ detail: '{title}' }}))")
        except Exception:
            pass

    dock.on_target_changed = on_target_title

    def on_loaded():
        hwnd = ctypes.windll.user32.FindWindowW(None, "微信聊天助手")
        if hwnd:
            # 添加 WS_EX_TOOLWINDOW 防止任务栏污染
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000080)
            dock.set_helper_hwnd(hwnd)
            dock.start()

    window.events.loaded += on_loaded
    webview.start(debug=False)

if __name__ == "__main__":
    create_app()
