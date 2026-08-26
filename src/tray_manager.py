import ctypes
from ctypes import wintypes
import threading
import os
import sys

class Win32NativeTray:
    """
    纯 Win32 原生托盘图标管理器 (infi.systray 经典可靠模型)
    零外部依赖（彻底摆脱 PIL、Pillow、pystray 庞大体积），体积缩减数十兆
    使用 Microsoft 推荐的 InsertMenuItemW + MENUITEMINFOW 原生系统标准菜单
    """
    WM_USER = 0x0400
    WM_TRAY = WM_USER + 20
    WM_COMMAND = 0x0111
    WM_RBUTTONUP = 0x0205
    WM_LBUTTONUP = 0x0202
    WM_LBUTTONDBLCLK = 0x0203
    WM_DESTROY = 0x0002
    WM_NULL = 0x0000

    NIM_ADD = 0x00000000
    NIM_MODIFY = 0x00000001
    NIM_DELETE = 0x00000002

    NIF_MESSAGE = 0x00000001
    NIF_ICON = 0x00000002
    NIF_TIP = 0x00000004

    MIIM_STATE = 0x00000001
    MIIM_ID = 0x00000002
    MIIM_SUBMENU = 0x00000004
    MIIM_CHECKMARKS = 0x00000008
    MIIM_TYPE = 0x00000010
    MIIM_DATA = 0x00000020
    MIIM_STRING = 0x00000040
    MIIM_BITMAP = 0x00000080
    MIIM_FTYPE = 0x00000100

    MF_STRING = 0x00000000
    MF_SEPARATOR = 0x00000800
    TPM_LEFTALIGN = 0x0000
    TPM_RIGHTBUTTON = 0x0002

    ID_TOGGLE = 1001
    ID_EXIT = 1002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    shell32 = ctypes.windll.shell32
    gdi32 = ctypes.windll.gdi32

    class NOTIFYICONDATAW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("hWnd", wintypes.HWND),
            ("uID", wintypes.UINT),
            ("uFlags", wintypes.UINT),
            ("uCallbackMessage", wintypes.UINT),
            ("hIcon", wintypes.HICON),
            ("szTip", wintypes.WCHAR * 128),
            ("dwState", wintypes.DWORD),
            ("dwStateMask", wintypes.DWORD),
            ("szInfo", wintypes.WCHAR * 256),
            ("uTimeoutOrVersion", wintypes.UINT),
            ("szInfoTitle", wintypes.WCHAR * 64),
            ("dwInfoFlags", wintypes.DWORD),
        ]

    class WNDCLASSEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("style", wintypes.UINT),
            ("lpfnWndProc", ctypes.c_void_p),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HICON),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
            ("hIconSm", wintypes.HICON),
        ]

    class MENUITEMINFOW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("fMask", wintypes.UINT),
            ("fType", wintypes.UINT),
            ("fState", wintypes.UINT),
            ("wID", wintypes.UINT),
            ("hSubMenu", wintypes.HMENU),
            ("hbmpChecked", wintypes.HBITMAP),
            ("hbmpUnchecked", wintypes.HBITMAP),
            ("dwItemData", ctypes.c_ulonglong),
            ("dwTypeData", ctypes.c_wchar_p),
            ("cch", wintypes.UINT),
            ("hbmpItem", wintypes.HBITMAP),
        ]

    class ICONINFO(ctypes.Structure):
        _fields_ = [
            ("fIcon", wintypes.BOOL),
            ("xHotspot", wintypes.DWORD),
            ("yHotspot", wintypes.DWORD),
            ("hbmMask", wintypes.HBITMAP),
            ("hbmColor", wintypes.HBITMAP),
        ]

    # 显式声明 Win32 64-bit 原型
    user32.CreatePopupMenu.restype = wintypes.HMENU
    user32.InsertMenuItemW.argtypes = [wintypes.HMENU, wintypes.UINT, wintypes.BOOL, ctypes.POINTER(MENUITEMINFOW)]
    user32.InsertMenuItemW.restype = wintypes.BOOL
    user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, ctypes.c_void_p]
    user32.TrackPopupMenu.restype = wintypes.BOOL
    user32.DestroyMenu.argtypes = [wintypes.HMENU]
    user32.DestroyMenu.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DefWindowProcW.restype = ctypes.c_longlong
    user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.LoadImageW.restype = wintypes.HANDLE

    def __init__(self, on_toggle=None, on_exit=None):
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.hwnd = 0
        self.h_icon = 0
        self._thread = None
        self._wndproc = None

    def _pack_menu_item(self, text=None, w_id=None, f_type=None) -> MENUITEMINFOW:
        res = self.MENUITEMINFOW()
        res.cbSize = ctypes.sizeof(self.MENUITEMINFOW)
        res.fMask = 0
        if text is not None:
            res.fMask |= self.MIIM_STRING
            res.fType = self.MF_STRING
            res.dwTypeData = text
            res.cch = len(text)
        if w_id is not None:
            res.fMask |= self.MIIM_ID
            res.wID = w_id
        if f_type is not None:
            res.fMask |= self.MIIM_FTYPE
            res.fType = f_type
        return res

    def _get_app_icon(self) -> int:
        """加载 app.ico 作为托盘高清图标，若缺失则回退至 GDI 动态标"""
        candidates = [
            os.path.join(getattr(sys, "_MEIPASS", ""), "app.ico"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.ico"),
            os.path.join(os.getcwd(), "app.ico"),
            os.path.join(os.path.dirname(sys.executable), "app.ico"),
        ]
        for path in candidates:
            if path and os.path.exists(path):
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                LR_DEFAULTSIZE = 0x00000040
                h_icon = self.user32.LoadImageW(
                    0, path, IMAGE_ICON, 0, 0,
                    LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
                if h_icon:
                    return h_icon
        return self._create_green_icon()

    def _create_green_icon(self) -> int:
        """纯 GDI 动态绘制高品质绿色对话气泡托盘图标"""
        hdc = self.user32.GetDC(0)
        mem_dc = self.gdi32.CreateCompatibleDC(hdc)
        mask_dc = self.gdi32.CreateCompatibleDC(hdc)

        hbm_color = self.gdi32.CreateCompatibleBitmap(hdc, 32, 32)
        hbm_mask = self.gdi32.CreateBitmap(32, 32, 1, 1, None)

        old_color = self.gdi32.SelectObject(mem_dc, hbm_color)
        old_mask = self.gdi32.SelectObject(mask_dc, hbm_mask)

        # 绿色背景画刷 #07C160 (RGB: 7, 193, 96 -> BGR: 0x60C107)
        green_brush = self.gdi32.CreateSolidBrush(0x0060C107)
        white_brush = self.gdi32.CreateSolidBrush(0x00FFFFFF)
        black_brush = self.gdi32.CreateSolidBrush(0x00000000)
        null_pen = self.gdi32.GetStockObject(8) # NULL_PEN

        # 1. 绘制透明掩码底板
        self.gdi32.SelectObject(mask_dc, white_brush)
        self.gdi32.SelectObject(mask_dc, null_pen)
        self.gdi32.Rectangle(mask_dc, 0, 0, 33, 33)

        # 掩码中挖出圆形可见区域
        self.gdi32.SelectObject(mask_dc, black_brush)
        self.gdi32.Ellipse(mask_dc, 1, 1, 31, 31)

        # 2. 彩色位图中绘制绿色圆形与白色居中气泡
        self.gdi32.SelectObject(mem_dc, green_brush)
        self.gdi32.SelectObject(mem_dc, null_pen)
        self.gdi32.Ellipse(mem_dc, 1, 1, 31, 31)

        self.gdi32.SelectObject(mem_dc, white_brush)
        self.gdi32.RoundRect(mem_dc, 7, 8, 25, 21, 4, 4)

        # 清理 GDI 对象
        self.gdi32.SelectObject(mem_dc, old_color)
        self.gdi32.SelectObject(mask_dc, old_mask)
        self.gdi32.DeleteDC(mem_dc)
        self.gdi32.DeleteDC(mask_dc)
        self.user32.ReleaseDC(0, hdc)
        self.gdi32.DeleteObject(green_brush)
        self.gdi32.DeleteObject(white_brush)
        self.gdi32.DeleteObject(black_brush)

        icon_info = self.ICONINFO()
        icon_info.fIcon = True
        icon_info.xHotspot = 0
        icon_info.yHotspot = 0
        icon_info.hbmMask = hbm_mask
        icon_info.hbmColor = hbm_color

        h_icon = self.user32.CreateIconIndirect(ctypes.byref(icon_info))
        self.gdi32.DeleteObject(hbm_color)
        self.gdi32.DeleteObject(hbm_mask)
        return h_icon

    def _show_menu(self):
        h_menu = self.user32.CreatePopupMenu()
        
        item1 = self._pack_menu_item(text="显示 / 隐藏助手", w_id=self.ID_TOGGLE)
        self.user32.InsertMenuItemW(h_menu, 0, 1, ctypes.byref(item1))

        item2 = self._pack_menu_item(f_type=self.MF_SEPARATOR)
        self.user32.InsertMenuItemW(h_menu, 1, 1, ctypes.byref(item2))

        item3 = self._pack_menu_item(text="退出助手程序", w_id=self.ID_EXIT)
        self.user32.InsertMenuItemW(h_menu, 2, 1, ctypes.byref(item3))

        pt = wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(pt))
        self.user32.SetForegroundWindow(self.hwnd)
        
        self.user32.TrackPopupMenu(
            h_menu,
            self.TPM_LEFTALIGN | self.TPM_RIGHTBUTTON,
            pt.x, pt.y, 0, self.hwnd, None
        )
        self.user32.PostMessageW(self.hwnd, self.WM_NULL, 0, 0)
        self.user32.DestroyMenu(h_menu)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == self.WM_TRAY:
            if lparam in (self.WM_LBUTTONUP, self.WM_LBUTTONDBLCLK):
                if callable(self.on_toggle):
                    self.on_toggle()
            elif lparam == self.WM_RBUTTONUP:
                self._show_menu()
            return 0
        elif msg == self.WM_COMMAND:
            cmd = wparam & 0xFFFF
            if cmd == self.ID_TOGGLE:
                if callable(self.on_toggle):
                    self.on_toggle()
            elif cmd == self.ID_EXIT:
                if callable(self.on_exit):
                    self.on_exit()
            return 0
        elif msg == self.WM_DESTROY:
            self.stop()
            self.user32.PostQuitMessage(0)
            return 0

        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _run_loop(self):
        h_inst = self.kernel32.GetModuleHandleW(None)
        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        self._wndproc = WNDPROC(self._wnd_proc)

        self.h_icon = self._get_app_icon()

        cls_name = "ChatHelper_NativeTray_Class"
        wc = self.WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(self.WNDCLASSEXW)
        wc.lpfnWndProc = ctypes.cast(self._wndproc, ctypes.c_void_p).value
        wc.hInstance = h_inst
        wc.hIcon = self.h_icon
        wc.hIconSm = self.h_icon
        wc.lpszClassName = cls_name
        self.user32.RegisterClassExW(ctypes.byref(wc))

        self.hwnd = self.user32.CreateWindowExW(
            0, cls_name, "ChatHelper_TrayWnd", 0,
            0, 0, 0, 0, 0, 0, h_inst, None
        )

        nid = self.NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(self.NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = self.NIF_MESSAGE | self.NIF_ICON | self.NIF_TIP
        nid.uCallbackMessage = self.WM_TRAY
        nid.hIcon = self.h_icon
        nid.szTip = "微信聊天助手"

        self.shell32.Shell_NotifyIconW(self.NIM_ADD, ctypes.byref(nid))

        msg = wintypes.MSG()
        while self.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            self.user32.TranslateMessage(ctypes.byref(msg))
            self.user32.DispatchMessageW(ctypes.byref(msg))

    def start(self):
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if self.hwnd:
            nid = self.NOTIFYICONDATAW()
            nid.cbSize = ctypes.sizeof(self.NOTIFYICONDATAW)
            nid.hWnd = self.hwnd
            nid.uID = 1
            self.shell32.Shell_NotifyIconW(self.NIM_DELETE, ctypes.byref(nid))
            self.hwnd = 0
        if self.h_icon:
            self.user32.DestroyIcon(self.h_icon)
            self.h_icon = 0

TrayManager = Win32NativeTray
