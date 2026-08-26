import ctypes
from ctypes import wintypes
import time
import os

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

    # 配置 64 位 ctypes 完整类型签名，防止内存截断与隐式类型崩溃
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.restype = wintypes.HGLOBAL

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL

    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = wintypes.BOOL

    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE

    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL

    user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
    user32.RegisterClipboardFormatW.restype = wintypes.UINT

    @classmethod
    def set_text(cls, text: str, max_retries: int = 10) -> bool:
        encoded = (str(text) + "\0").encode("utf-16le")
        total_len = len(encoded)

        for _ in range(max_retries):
            h_mem = cls.kernel32.GlobalAlloc(cls.GHND, total_len)
            if not h_mem:
                time.sleep(0.01)
                continue

            p_mem = cls.kernel32.GlobalLock(h_mem)
            if p_mem:
                ctypes.memmove(p_mem, encoded, total_len)
                cls.kernel32.GlobalUnlock(h_mem)

                if cls.user32.OpenClipboard(None):
                    try:
                        cls.user32.EmptyClipboard()
                        cls.user32.SetClipboardData(cls.CF_UNICODETEXT, h_mem)
                        return True
                    finally:
                        cls.user32.CloseClipboard()
                else:
                    cls.kernel32.GlobalFree(h_mem)

            time.sleep(0.015)
        return False

    @classmethod
    def set_files(cls, file_paths: list[str], max_retries: int = 10) -> bool:
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
        drop_effect_fmt = cls.user32.RegisterClipboardFormatW("Preferred DropEffect")

        for _ in range(max_retries):
            h_mem = cls.kernel32.GlobalAlloc(cls.GHND, total_len)
            if not h_mem:
                time.sleep(0.01)
                continue

            p_mem = cls.kernel32.GlobalLock(h_mem)
            if p_mem:
                ctypes.memmove(p_mem, total_bytes, total_len)
                cls.kernel32.GlobalUnlock(h_mem)

                # 设置 Preferred DropEffect = 1 (DROPEFFECT_COPY)
                h_effect = cls.kernel32.GlobalAlloc(cls.GHND, 4)
                if h_effect:
                    p_effect = cls.kernel32.GlobalLock(h_effect)
                    if p_effect:
                        ctypes.c_uint32.from_address(p_effect).value = 1
                        cls.kernel32.GlobalUnlock(h_effect)

                if cls.user32.OpenClipboard(None):
                    try:
                        cls.user32.EmptyClipboard()
                        if h_effect:
                            cls.user32.SetClipboardData(drop_effect_fmt, h_effect)
                        cls.user32.SetClipboardData(cls.CF_HDROP, h_mem)
                        return True
                    finally:
                        cls.user32.CloseClipboard()
                else:
                    cls.kernel32.GlobalFree(h_mem)
                    if h_effect:
                        cls.kernel32.GlobalFree(h_effect)

            time.sleep(0.015)
        return False
