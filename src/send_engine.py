import time
import datetime
import os
import ctypes
from src.win32_clipboard import Win32Clipboard

class SendEngine:
    VK_CONTROL = 0x11
    VK_RETURN = 0x0D
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002

    user32 = ctypes.windll.user32

    def interpolate_variables(self, template: str, extra_vars: dict = None) -> str:
        now = datetime.datetime.now()
        hour = now.hour
        if 5 <= hour < 9:
            greeting = "早上好"
        elif 9 <= hour < 12:
            greeting = "上午好"
        elif 12 <= hour < 14:
            greeting = "中午好"
        elif 14 <= hour < 18:
            greeting = "下午好"
        else:
            greeting = "晚上好"

        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        mapping = {
            "{日期}": now.strftime("%Y-%m-%d"),
            "{时间}": now.strftime("%H:%M:%S"),
            "{星期}": weekdays[now.weekday()],
            "{问候语}": greeting,
            "{年}": str(now.year),
            "{月}": f"{now.month:02d}",
            "{日}": f"{now.day:02d}",
        }
        if extra_vars:
            for k, v in extra_vars.items():
                tag = k if k.startswith("{") else f"{{{k}}}"
                mapping[tag] = str(v)

        result = str(template or "")
        for tag, val in mapping.items():
            result = result.replace(tag, str(val))
        return result

    def _activate_window(self, hwnd: int) -> bool:
        try:
            self.user32.SwitchToThisWindow(hwnd, True)
            self.user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def _simulate_paste(self, delay_ms: int = 120) -> None:
        time.sleep(delay_ms / 1000.0)
        self.user32.keybd_event(self.VK_CONTROL, 0, 0, 0)
        self.user32.keybd_event(self.VK_V, 0, 0, 0)
        self.user32.keybd_event(self.VK_V, 0, self.KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(self.VK_CONTROL, 0, self.KEYEVENTF_KEYUP, 0)

    def _simulate_enter(self, delay_ms: int = 120) -> None:
        time.sleep(delay_ms / 1000.0)
        self.user32.keybd_event(self.VK_RETURN, 0, 0, 0)
        self.user32.keybd_event(self.VK_RETURN, 0, self.KEYEVENTF_KEYUP, 0)

    def send_payload(self, target_hwnd: int, text: str, attachments: list[dict], mode: str = "normal", delays: dict = None) -> bool:
        delays = delays or {}
        p_delay = int(delays.get("paste_delay", 120))
        e_delay = int(delays.get("enter_delay", 120))
        t_delay = int(delays.get("typewriter_delay", 500))
        r_delay = int(delays.get("repeat_delay", 500))

        # 1. 核心第一步：先将全部动态占位符（{日期}、{问候语}等）完全插值替换为真实文本
        interpolated_text = self.interpolate_variables(text)

        if not target_hwnd or not self.user32.IsWindow(target_hwnd):
            return False

        self._activate_window(target_hwnd)

        # 提取存在的有效本地附件路径
        valid_files = []
        for item in (attachments or []):
            path = item.get("path") if isinstance(item, dict) else str(item)
            if path and os.path.exists(path):
                valid_files.append(os.path.abspath(path))

        if mode == "paste_only":
            if interpolated_text:
                Win32Clipboard.set_text(interpolated_text)
                self._simulate_paste(p_delay)
            if valid_files:
                time.sleep(0.15)
                Win32Clipboard.set_files(valid_files)
                self._simulate_paste(p_delay)
            return True

        if mode == "reverse":
            interpolated_text = interpolated_text[::-1]

        if mode == "typewriter":
            # 2. 逐字单条发送：先完成占位符替换，再对最终文本逐字发送并回车（默认 500ms 间隔）
            for ch in interpolated_text:
                if ch == "\r":
                    continue
                if ch == "\n":
                    time.sleep(t_delay / 1000.0)
                    continue

                try:
                    if Win32Clipboard.set_text(ch):
                        self._simulate_paste(35)
                        self._simulate_enter(40)
                except Exception:
                    pass
                time.sleep(t_delay / 1000.0)

            if valid_files:
                Win32Clipboard.set_files(valid_files)
                self._simulate_paste(200)
                self._simulate_enter(500)
            return True

        repeat_count = 3 if mode == "repeat3" else 1
        for idx in range(repeat_count):
            if interpolated_text:
                Win32Clipboard.set_text(interpolated_text)
                self._simulate_paste(p_delay)
                self._simulate_enter(e_delay)

            # 发送多附件（支持批量注入与可靠延时）
            if valid_files:
                time.sleep(0.1)
                Win32Clipboard.set_files(valid_files)
                # 微信粘贴文件前置延时
                self._simulate_paste(max(p_delay, 200))
                # 微信客户端加载文件需要生成缩略图与校验，回车延时需充足（500ms）
                self._simulate_enter(max(e_delay, 500))

            # 连发 3 次模式下的轮次间隔（默认 500ms）
            if idx < repeat_count - 1:
                time.sleep(r_delay / 1000.0)

        return True
