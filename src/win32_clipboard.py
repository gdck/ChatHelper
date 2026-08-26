import ctypes
from ctypes import wintypes
import time
import os

try:
    import win32clipboard
    import win32con
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]

class Win32Clipboard:
    CF_UNICODETEXT = 13
    CF_HDROP = 15
    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040
    GHND = GMEM_MOVEABLE | GMEM_ZEROINIT

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # 配置 64 位 ctypes 签名
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL

    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = wintypes.BOOL

    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE

    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL

    @classmethod
    def set_text(cls, text: str, max_retries: int = 5) -> bool:
        if HAS_PYWIN32:
            for _ in range(max_retries):
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                    return True
                except Exception:
                    time.sleep(0.05)
                finally:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass
            return False

        # Fallback ctypes
        encoded = text.encode("utf-16le") + b"\0\0"
        for _ in range(max_retries):
            if cls.user32.OpenClipboard(None):
                try:
                    cls.user32.EmptyClipboard()
                    h_mem = cls.kernel32.GlobalAlloc(cls.GHND, len(encoded))
                    if h_mem:
                        p_mem = cls.kernel32.GlobalLock(h_mem)
                        if p_mem:
                            ctypes.memmove(p_mem, encoded, len(encoded))
                            cls.kernel32.GlobalUnlock(h_mem)
                            cls.user32.SetClipboardData(cls.CF_UNICODETEXT, h_mem)
                            return True
                finally:
                    cls.user32.CloseClipboard()
            time.sleep(0.05)
        return False

    @classmethod
    def set_files(cls, file_paths: list[str], max_retries: int = 5) -> bool:
        valid_paths = [os.path.abspath(p) for p in file_paths if os.path.exists(p)]
        if not valid_paths:
            return False

        files_bytes = "\0".join(valid_paths).encode("utf-16le") + b"\0\0\0\0"
        dropfiles = DROPFILES()
        dropfiles.pFiles = ctypes.sizeof(DROPFILES)
        dropfiles.pt = wintypes.POINT(0, 0)
        dropfiles.fNC = False
        dropfiles.fWide = True

        total_bytes = bytes(dropfiles) + files_bytes
        total_len = len(total_bytes)

        if HAS_PYWIN32:
            for _ in range(max_retries):
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_HDROP, total_bytes)
                    return True
                except Exception:
                    time.sleep(0.05)
                finally:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass
            return False

        # Fallback ctypes
        for _ in range(max_retries):
            if cls.user32.OpenClipboard(None):
                try:
                    cls.user32.EmptyClipboard()
                    h_mem = cls.kernel32.GlobalAlloc(cls.GHND, total_len)
                    if h_mem:
                        p_mem = cls.kernel32.GlobalLock(h_mem)
                        if p_mem:
                            ctypes.memmove(p_mem, total_bytes, total_len)
                            cls.kernel32.GlobalUnlock(h_mem)
                            cls.user32.SetClipboardData(cls.CF_HDROP, h_mem)
                            return True
                finally:
                    cls.user32.CloseClipboard()
            time.sleep(0.05)
        return False
