import os
import sys
import ctypes

# 确保项目根目录在 sys.path 中
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import webview
from src.database import DatabaseManager
from src.send_engine import SendEngine
from src.docking_engine import DockingEngine
from src.api import JsApi

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

    # 数据库路径：打包后放在 exe 同级目录，源码模式放在项目根目录
    if getattr(sys, 'frozen', False):
        db_dir = os.path.dirname(sys.executable)
    else:
        db_dir = BASE_DIR
    db_path = os.path.join(db_dir, "chat_helper.db")

    db = DatabaseManager(db_path)
    db.init_db()

    send = SendEngine()
    dock = DockingEngine(sidebar_width=408)
    api = JsApi(db, dock, send)

    # 前端资源路径探测
    html_path = get_resource_path(os.path.join("frontend", "dist", "index.html"))
    if os.path.exists(html_path):
        url = html_path
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
        on_top=True,
        transparent=True
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
