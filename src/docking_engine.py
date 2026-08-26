import ctypes
from ctypes import wintypes
import threading
import time
from dataclasses import dataclass

@dataclass
class TargetWindowInfo:
    hwnd: int
    title: str
    class_name: str
    process_name: str
    rect: tuple[int, int, int, int]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class DockingEngine:
    SWP_NOACTIVATE = 0x0010
    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    SWP_HIDEWINDOW = 0x0080

    SUPPORTED_PROCESSES = {
        "wechat.exe": ["WeChatMainWndForPC", "ChatWnd"],
        "wxwork.exe": ["WeWorkWindow"],
        "qq.exe": ["TXGuiFoundation"],
        "tim.exe": ["TXGuiFoundation"],
        "dingtalk.exe": ["StandardFrame_DingTalk"],
        "aliworkbench.exe": ["StandardFrame"],
    }

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    def __init__(self, sidebar_width: int = 408):
        self.sidebar_width = sidebar_width
        self.helper_hwnd: int = 0
        self.current_target_hwnd: int = 0
        self.collapsed: bool = False
        self.running: bool = False
        self._thread: threading.Thread | None = None
        self.on_target_changed = None

    def set_helper_hwnd(self, hwnd: int) -> None:
        self.helper_hwnd = hwnd

    def calculate_dock_pos(self, rect: tuple[int, int, int, int], collapsed: bool, sidebar_width: int = 408, icon_size: int = 32) -> tuple[int, int, int, int]:
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        if collapsed:
            return (right - icon_size, top - icon_size, icon_size, icon_size)
        else:
            return (right, top, sidebar_width, height)

    def _get_window_info(self, hwnd: int) -> TargetWindowInfo | None:
        if not hwnd or not self.user32.IsWindow(hwnd):
            return None
        rect = RECT()
        if not self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        
        length = self.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value

        class_buff = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, class_buff, 256)
        class_name = class_buff.value

        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        h_proc = self.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
        proc_name = ""
        if h_proc:
            name_buff = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            self.kernel32.QueryFullProcessImageNameW(h_proc, 0, name_buff, ctypes.byref(size))
            self.kernel32.CloseHandle(h_proc)
            proc_name = name_buff.value.split("\\")[-1].lower()

        return TargetWindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_name,
            process_name=proc_name,
            rect=(rect.left, rect.top, rect.right, rect.bottom)
        )

    def is_supported_target(self, info: TargetWindowInfo) -> bool:
        if not info or not info.title:
            return False
        for proc, classes in self.SUPPORTED_PROCESSES.items():
            if proc == info.process_name and info.class_name in classes:
                return True
        return False

    def update_dock_position(self, force: bool = False) -> None:
        if not self.helper_hwnd or not self.user32.IsWindow(self.helper_hwnd):
            return

        fg_hwnd = self.user32.GetForegroundWindow()
        if fg_hwnd == self.helper_hwnd:
            target_hwnd = self.current_target_hwnd
        else:
            target_hwnd = fg_hwnd

        info = self._get_window_info(target_hwnd)
        if info and self.is_supported_target(info):
            if target_hwnd != self.current_target_hwnd:
                self.current_target_hwnd = target_hwnd
                if callable(self.on_target_changed):
                    self.on_target_changed(info.title)

            x, y, w, h = self.calculate_dock_pos(info.rect, self.collapsed, self.sidebar_width)
            self.user32.SetWindowPos(
                self.helper_hwnd,
                0,
                x, y, w, h,
                self.SWP_NOACTIVATE | self.SWP_NOZORDER | self.SWP_SHOWWINDOW
            )
        else:
            if fg_hwnd != self.helper_hwnd:
                # 隐藏到屏幕外
                self.user32.SetWindowPos(
                    self.helper_hwnd,
                    0,
                    -10000, -10000, 10, 10,
                    self.SWP_NOACTIVATE | self.SWP_NOZORDER
                )

    def _loop(self) -> None:
        while self.running:
            try:
                self.update_dock_position()
            except Exception:
                pass
            time.sleep(0.04)

    def start(self) -> None:
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

    def toggle_collapse(self) -> bool:
        self.collapsed = not self.collapsed
        self.update_dock_position(force=True)
        return self.collapsed
