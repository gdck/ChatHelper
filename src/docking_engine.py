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
    """
    Win32 顶级事件驱动窗口吸附引擎 (Event-Driven Docking Architecture)
    1. SetWinEventHook OS 原生系统事件驱动：
       - EVENT_OBJECT_LOCATIONCHANGE (0 延迟跟手，拖动无卡顿撕裂)
       - EVENT_SYSTEM_FOREGROUND / MINIMIZE (焦点与最小化即时响应)
       - EVENT_OBJECT_NAMECHANGE (会话切换标题瞬时同步)
       - 静止状态 0% CPU 占用
    2. DWM 真实物理边框校准 (DWMWA_EXTENDED_FRAME_BOUNDS)：彻底消除 Windows 10/11 7px 阴影白边缝隙
    3. 400ms 兜底心跳保护，保障多屏幕/边缘场景 100% 稳定性
    """
    SWP_NOACTIVATE = 0x0010
    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    SWP_HIDEWINDOW = 0x0080

    EVENT_SYSTEM_FOREGROUND = 0x0003
    EVENT_SYSTEM_MINIMIZESTART = 0x0016
    EVENT_SYSTEM_MINIMIZEEND = 0x0017
    EVENT_OBJECT_DESTROY = 0x8001
    EVENT_OBJECT_LOCATIONCHANGE = 0x800B
    EVENT_OBJECT_NAMECHANGE = 0x800C

    WINEVENT_OUTOFCONTEXT = 0x0000
    WINEVENT_SKIPOWNPROCESS = 0x0002
    OBJID_WINDOW = 0x00000000

    DWMWA_EXTENDED_FRAME_BOUNDS = 9

    SUPPORTED_PROCESSES = {
        "wechat.exe": ["WeChatMainWndForPC", "ChatWnd", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "Qt5152QWindowIcon", "Qt6QWindowIcon"],
        "weixin.exe": ["WeixinMainWndForPC", "WeChatMainWndForPC", "ChatWnd", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "Qt5152QWindowIcon", "Qt6QWindowIcon", "Weixin"],
        "wxwork.exe": ["WeWorkWindow", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "qq.exe": ["TXGuiFoundation", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "tim.exe": ["TXGuiFoundation", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "dingtalk.exe": ["StandardFrame_DingTalk", "StandardFrame", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
        "aliworkbench.exe": ["StandardFrame", "Chrome_WidgetWin_0", "Chrome_WidgetWin_1"],
    }

    PROCESS_TO_KEY = {
        "wechat.exe": "wechat",
        "weixin.exe": "wechat",
        "wxwork.exe": "wxwork",
        "qq.exe": "qq",
        "tim.exe": "tim",
        "dingtalk.exe": "dingtalk",
        "aliworkbench.exe": "aliworkbench",
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
        "截图", "表情", "查看图片", "图片查看", "图片查看器", "设置", "系统设置", "文件传输", "关于",
        "查找", "加为好友", "消息盒子", "未读消息", "系统消息", "好友管理", "群管理",
        "Alert", "Notice", "Warning", "Confirm", "Login", "Settings"
    }

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    dwmapi = ctypes.windll.dwmapi

    WINEVENTPROC = ctypes.WINFUNCTYPE(
        None,
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.HWND,
        ctypes.c_long,
        ctypes.c_long,
        wintypes.DWORD,
        wintypes.DWORD,
    )

    user32.SetWinEventHook.argtypes = [
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HMODULE,
        WINEVENTPROC,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD
    ]
    user32.SetWinEventHook.restype = wintypes.HANDLE
    user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
    user32.UnhookWinEvent.restype = wintypes.BOOL

    dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long

    def __init__(self, sidebar_width: int = 480):
        self.sidebar_width = sidebar_width
        self.helper_hwnd: int = 0
        self.current_target_hwnd: int = 0
        self.current_target_title: str = ""
        self.collapsed: bool = False
        self.running: bool = False
        self._thread: threading.Thread | None = None
        self._hook_handle: int = 0
        self._hook_callback = None
        self.on_target_changed = None
        self._lock = threading.Lock()
        self.enabled_ims: set[str] = {"wechat", "wxwork", "qq", "tim", "dingtalk", "aliworkbench"}

    def set_enabled_ims(self, keys: list[str]) -> None:
        self.enabled_ims = set(keys)
        self.update_dock_position(force=True)

    def set_helper_hwnd(self, hwnd: int) -> None:
        self.helper_hwnd = hwnd

    def calculate_dock_pos(self, rect: tuple[int, int, int, int], collapsed: bool, sidebar_width: int = 408, icon_size: int = 28) -> tuple[int, int, int, int]:
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        if collapsed:
            return (right - icon_size, top - icon_size, icon_size, icon_size)
        else:
            return (right, top, sidebar_width, height)

    def _get_window_rect(self, hwnd: int) -> tuple[int, int, int, int] | None:
        """获取窗口物理矩形，优先通过 DWM 获取消除 7px 阴影后的精确可见边界"""
        if not hwnd or not self.user32.IsWindow(hwnd):
            return None
        rect = RECT()
        try:
            res = self.dwmapi.DwmGetWindowAttribute(hwnd, self.DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(RECT))
            if res == 0 and rect.right > rect.left and rect.bottom > rect.top:
                return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception:
            pass

        if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None

    def _get_window_info(self, hwnd: int) -> TargetWindowInfo | None:
        if not hwnd or not self.user32.IsWindow(hwnd):
            return None

        rect_tuple = self._get_window_rect(hwnd)
        if not rect_tuple:
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
        # 优先使用 PROCESS_QUERY_LIMITED_INFORMATION (0x1000)，不受 UAC 权限限制
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
            rect=rect_tuple
        )

    def is_supported_target(self, info: TargetWindowInfo) -> bool:
        if not info:
            return False

        # 1. 检查进程名是否属于支持的 IM 客户端
        p_name = (info.process_name or "").lower()
        matched_classes = None
        matched_key = None
        for proc, classes in self.SUPPORTED_PROCESSES.items():
            if proc in p_name:
                matched_classes = classes
                matched_key = self.PROCESS_TO_KEY.get(proc)
                break

        if matched_classes is None:
            # 模糊前缀匹配，排除非主界面的辅助进程（如 WeChatAppEx/QQExternal）
            if "weixin" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["weixin.exe"]
                matched_key = "wechat"
            elif "wechat" in p_name and not "wechatappex" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["wechat.exe"]
                matched_key = "wechat"
            elif "wxwork" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["wxwork.exe"]
                matched_key = "wxwork"
            elif "qq" in p_name and not "qqexternal" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["qq.exe"]
                matched_key = "qq"
            elif "tim" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["tim.exe"]
                matched_key = "tim"
            elif "dingtalk" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["dingtalk.exe"]
                matched_key = "dingtalk"
            elif "aliworkbench" in p_name:
                matched_classes = self.SUPPORTED_PROCESSES["aliworkbench.exe"]
                matched_key = "aliworkbench"
            else:
                return False

        # 检查该 IM 是否在用户启用的支持列表中
        if matched_key and matched_key not in self.enabled_ims:
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

    def update_dock_position(self, target_hwnd: int | None = None, force: bool = False) -> None:
        if not self.helper_hwnd or not self.user32.IsWindow(self.helper_hwnd):
            return

        with self._lock:
            if target_hwnd is None:
                fg_hwnd = self.user32.GetForegroundWindow()
                if fg_hwnd == self.helper_hwnd:
                    target_hwnd = self.current_target_hwnd
                else:
                    target_hwnd = fg_hwnd

            info = self._get_window_info(target_hwnd)
            if info and self.is_supported_target(info):
                # 友好标题展示
                if info.title:
                    display_title = info.title
                else:
                    display_title = self.PROCESS_DISPLAY_NAMES.get(info.process_name, info.process_name.replace(".exe", "").upper())

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
                fg_hwnd = self.user32.GetForegroundWindow()
                if fg_hwnd != self.helper_hwnd and target_hwnd == fg_hwnd:
                    # 隐藏到屏幕外
                    self.user32.SetWindowPos(
                        self.helper_hwnd,
                        0,
                        -10000, -10000, 10, 10,
                        self.SWP_NOACTIVATE | self.SWP_NOZORDER
                    )

    def _on_win_event(self, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        """OS 原生事件回调函数（0ms 极速响应）"""
        if not self.running or not hwnd:
            return

        try:
            if event == self.EVENT_SYSTEM_FOREGROUND:
                self.update_dock_position(target_hwnd=hwnd)
            elif event in (self.EVENT_OBJECT_LOCATIONCHANGE, self.EVENT_OBJECT_NAMECHANGE):
                if idObject == self.OBJID_WINDOW:
                    if hwnd == self.current_target_hwnd:
                        self.update_dock_position(target_hwnd=hwnd)
            elif event == self.EVENT_SYSTEM_MINIMIZESTART:
                if hwnd == self.current_target_hwnd and self.helper_hwnd:
                    self.user32.SetWindowPos(
                        self.helper_hwnd, 0, -10000, -10000, 10, 10,
                        self.SWP_NOACTIVATE | self.SWP_NOZORDER
                    )
            elif event == self.EVENT_SYSTEM_MINIMIZEEND:
                if hwnd == self.current_target_hwnd:
                    self.update_dock_position(target_hwnd=hwnd)
            elif event == self.EVENT_OBJECT_DESTROY:
                if hwnd == self.current_target_hwnd:
                    self.current_target_hwnd = 0
                    self.current_target_title = ""
                    if self.helper_hwnd:
                        self.user32.SetWindowPos(
                            self.helper_hwnd, 0, -10000, -10000, 10, 10,
                            self.SWP_NOACTIVATE | self.SWP_NOZORDER
                        )
        except Exception:
            pass

    def _hook_loop(self) -> None:
        """事件驱动消息泵与低频安全心跳"""
        self._hook_callback = self.WINEVENTPROC(self._on_win_event)
        self._hook_handle = self.user32.SetWinEventHook(
            0x0001, # EVENT_MIN
            0x800C, # EVENT_OBJECT_NAMECHANGE
            0,
            self._hook_callback,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT | self.WINEVENT_SKIPOWNPROCESS
        )

        msg = wintypes.MSG()
        last_heartbeat = time.time()

        while self.running:
            # 处理 Windows 事件队列
            while self.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))

            # 400ms 低频安全兜底心跳
            now = time.time()
            if now - last_heartbeat > 0.4:
                try:
                    self.update_dock_position()
                except Exception:
                    pass
                last_heartbeat = now

            time.sleep(0.02)

        if self._hook_handle:
            self.user32.UnhookWinEvent(self._hook_handle)
            self._hook_handle = 0

    def find_first_running_target_hwnd(self) -> int:
        """扫描当前系统中是否存在已打开且受支持的有效 IM 聊天窗口"""
        found = 0
        def enum_cb(hwnd, lparam):
            nonlocal found
            if not self.user32.IsWindowVisible(hwnd):
                return True
            info = self._get_window_info(hwnd)
            if info and self.is_supported_target(info):
                found = hwnd
                return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return found

    def activate_target_or_hide(self) -> None:
        """
        启动智能贴靠与静默驻留机制：
        1. 优先扫描检测系统内是否已存在支持的 IM 窗口（如微信、QQ等）；
        2. 若存在，激活该 IM 窗口并无缝吸附于其右侧；
        3. 若不存在，将助手窗口静默隐藏至屏幕外，纯后台托盘驻留，绝不独立弹出孤立窗口。
        """
        target_hwnd = self.find_first_running_target_hwnd()
        if target_hwnd:
            if self.user32.IsIconic(target_hwnd):
                self.user32.ShowWindow(target_hwnd, 9) # SW_RESTORE
            else:
                self.user32.ShowWindow(target_hwnd, 5) # SW_SHOW

            try:
                self.user32.AllowSetForegroundWindow(-1)
                self.user32.SetForegroundWindow(target_hwnd)
            except Exception:
                pass

            self.update_dock_position(target_hwnd=target_hwnd, force=True)
        else:
            if self.helper_hwnd and self.user32.IsWindow(self.helper_hwnd):
                self.user32.SetWindowPos(
                    self.helper_hwnd,
                    0,
                    -10000, -10000, 10, 10,
                    self.SWP_NOACTIVATE | self.SWP_NOZORDER
                )

    def start(self) -> None:
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._hook_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

    def toggle_collapse(self) -> bool:
        self.collapsed = not self.collapsed
        self.update_dock_position(force=True)
        return self.collapsed
