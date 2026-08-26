---
name: win32-python-best-practices
description: "Best practices for Win32 API interop in 64-bit Python and pywebview desktop assistant architecture"
---

# Win32 Python & pywebview 开发实践守则

## 1. 64 位 Windows 下 ctypes 内存与指针安全规范
在 64 位 Python 中调用 Win32 原生 API 时，必须严格显式声明 `.argtypes` 与 `.restype`，严禁依赖默认 32 位整型（`c_int`）返回：

```python
import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

# 必须显式声明 64 位指针/句柄类型
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p

kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL

user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
```
* **剪贴板优先选用**：对于 `CF_HDROP` 多文件和 `CF_UNICODETEXT` 文本，优先采用 `win32clipboard`，ctypes 作为备选。

---

## 2. pywebview 桌面辅助吸附与跟随工具架构准则
开发吸附于第三方客户端（如微信、企微、QQ、钉钉）的桌面工具时：
1. **窗口跟随物理直操**：在 pywebview 窗口就绪后，通过 `FindWindowW` 获取宿主 Win32 HWND，直接在 Python 后台线程调用 `SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOACTIVATE | SWP_NOZORDER | SWP_SHOWWINDOW)` 进行贴边跟随，禁止走 JS-Python RPC 往返，杜绝渲染撕裂。
2. **任务栏与焦点保护**：给 pywebview 宿主 HWND 添加 `WS_EX_TOOLWINDOW` 扩展样式（`style | 0x00000080`），防止任务栏出现多余图标与焦点抢占。
3. **单例互斥锁**：启动时使用 `kernel32.CreateMutexW` 创建命名互斥体，防止重复启动实例。
