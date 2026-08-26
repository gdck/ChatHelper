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
        "wechat.exe": ["WeChatMainWndForPC", "ChatWnd", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "Qt5152QWindowIcon", "Qt6QWindowIcon"],
        "weixin.exe": ["WeixinMainWndForPC", "WeChatMainWndForPC", "ChatWnd", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "Qt5152QWindowIcon", "Qt6QWindowIcon", "Weixin"],
        "wxwork.exe": ["WeWorkWindow", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "qq.exe": ["TXGuiFoundation", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "tim.exe": ["TXGuiFoundation", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "dingtalk.exe": ["StandardFrame_DingTalk", "StandardFrame", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "aliworkbench.exe": ["StandardFrame", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
    }

    PROCESS_DISPLAY_NAMES = {
        "qq.exe": "QQ",
        "tim.exe": "TIM",
        "weixin.exe": "微信",
        "wechat.exe": "微信",
        "wxwork.exe": "企业微信",
        "dingtalk.exe": "钉钉",
        "aliworkbench.exe": "千牛"
    }

    EXCLUDED_TITLES = {
        "提示", "确认", "警告", "错误", "删除", "登录", "QQ登录", "退出", "转发",
        "截图", "表情", "查看图片", "图片查看器", "设置", "系统设置", "文件传输", "关于",
        "查找", "加为好友", "消息盒子", "未读消息", "系统消息", "好友管理", "群管理",
        "Alert", "Notice", "Warning", "Confirm", "Login", "Settings"
    }

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    def __init__(self, sidebar_width: int = 480):
        self.sidebar_width = sidebar_width
        self.helper_hwnd: int = 0
        self.current_target_hwnd: int = 0
        self.current_target_title: str = ""
        self.collapsed: bool = False
        self.running: bool = False
        self._thread: threading.Thread | None = None
        self.on_target_changed = None

    def set_helper_hwnd(self, hwnd: int) -> None:
        self.helper_hwnd = hwnd

    def calculate_dock_pos(self, rect: tuple[int, int, int, int], collapsed: bool, sidebar_width: int = 408, icon_size: int = 28) -> tuple[int, int, int, int]:
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        if collapsed:
            # 严格对齐 Delphi 原版坐标逻辑：r.Left + r.Width - 28, r.Top - 28, 28, 28
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
        title = buff.value.strip()

        class_buff = ctypes.create_unicode_buffer(512)
        self.user32.GetClassNameW(hwnd, class_buff, 512)
        class_name = class_buff.value.strip()

        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        proc_name = ""
        # 优先使用 PROCESS_QUERY_LIMITED_INFORMATION (0x1000)，不受 UAC/进程权限限制
        h_proc = self.kernel32.OpenProcess(0x1000, False, pid)
        if not h_proc:
            h_proc = self.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)

        if h_proc:
            name_buff = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            if self.kernel32.QueryFullProcessImageNameW(h_proc, 0, name_buff, ctypes.byref(size)):
                proc_name = name_buff.value.split("\\")[-1].lower()
            self.kernel32.CloseHandle(h_proc)

        # 托底方案：若 OpenProcess 失败，使用 psutil 获取进程名称
        if not proc_name and pid.value:
            try:
                import psutil
                proc_name = psutil.Process(pid.value).name().lower()
            except Exception:
                pass

        return TargetWindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_name,
            process_name=proc_name,
            rect=(rect.left, rect.top, rect.right, rect.bottom)
        )

    def is_supported_target(self, info: TargetWindowInfo) -> bool:
        if not info:
            return False

        # 1. 检查进程名是否属于支持的 IM 客户端
        p_name = (info.process_name or "").lower()
        matched_classes = None
        for proc, classes in self.SUPPORTED_PROCESSES.items():
            if proc in p_name:
                matched_classes = classes
                break

        if matched_classes is None:
            # 模糊前缀匹配，排除非主界面的辅助进程（如 WeChatAppEx/QQExternal）
            if "weixin" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["weixin.exe"]
            elif "wechat" in p_name and not "wechatappex" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["wechat.exe"]
            elif "wxwork" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["wxwork.exe"]
            elif "qq" in p_name and not "qqexternal" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["qq.exe"]
            elif "tim" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["tim.exe"]
            elif "dingtalk" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["dingtalk.exe"]
            elif "aliworkbench" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["aliworkbench.exe"]
            else:
                return False

        # 2. 过滤无效弹窗/提示框标题
        clean_title = (info.title or "").strip()
        if clean_title in self.EXCLUDED_TITLES:
            return False

        # 3. 过滤过小尺寸的弹窗（正常会话主窗体宽 >= 420，高 >= 320）
        left, top, right, bottom = info.rect
        width = right - left
        height = bottom - top
        if width < 420 or height < 320:
            return False

        # 4. 检查类名：命中显式类名或现代 UI 动态类名
        if info.class_name in matched_classes:
            return True

        c_lower = info.class_name.lower()
        if any(k in c_lower for k in ["wechat", "weixin", "chat", "chrome_widgetwin", "qt", "txgui", "standardframe"]):
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
            # 获取友好展示标题：优先取真实窗口标题，无标题时取软件友好名（如 QQ、微信）
            if info.title:
                display_title = info.title
            else:
                display_title = self.PROCESS_DISPLAY_NAMES.get(info.process_name, info.process_name.replace(".exe", "").upper())

            # 实时检测：无论是窗口句柄切换，还是在同一软件内切换会话导致标题变化，均实时通知前端
            if target_hwnd != self.current_target_hwnd or display_title != self.current_target_title:
                self.current_target_hwnd = target_hwnd
                self.current_target_title = display_title
                if callable(self.on_target_changed):
                    self.on_target_changed(display_title)

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
