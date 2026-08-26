# Python + pywebview 微信聊天助手重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 Python 3 + pywebview + Vue 3 技术栈，全新重构 Delphi 版“微信多开聊天助手”，实现目标聊天窗口原生级无缝贴边吸附、无限多附件与变量混合模拟发送、现代化毛玻璃界面与绿色便携打包。

**Architecture:** 
后端采用 Python 构建 Win32 原生吸附引擎（`SetWinEventHook` + `SetWindowPos` 直操底层 HWND 避免渲染延迟）、剪贴板多格式注入服务（`CF_HDROP` + `SendInput`）与 SQLite3 结构化数据存储；前端采用 Vue 3 + Vite 构建现代化暗黑/明亮自适应单页应用；通过 `pywebview.api` 桥接双向通信，并辅以 `pystray` 托盘与全局热键。

**Tech Stack:**
- **后端**: Python 3.10+, pywebview (Edge WebView2), ctypes / pywin32, pystray, keyboard / pynput, sqlite3
- **前端**: Vue 3 (Composition API), Vite, Modern Glassmorphism CSS, Lucide Icons
- **打包**: PyInstaller / Nuitka, Vite Build

**Spec:** `docs/superpowers/specs/2026-08-26-chathelper-python-pywebview-design.md`

## Global Constraints

- **运行平台**: Windows 10 / Windows 11 (64-bit)
- **目标宿主适配**: 微信 (`wechat.exe` / `WeChatMainWndForPC`), 企业微信 (`wxwork.exe` / `WeWorkWindow`), QQ (`qq.exe` / `TXGuiFoundation`), TIM (`tim.exe`), 钉钉 (`dingtalk.exe` / `StandardFrame_DingTalk`), 千牛 (`aliworkbench.exe` / `StandardFrame`)
- **吸附原则**: 贴边跟随必须在 Python 线程层直接操纵 Win32 HWND，禁止经由 JS 桥接往返计算坐标以规避延迟抖动。
- **无破坏发送**: 剪贴板注入后毫秒级激活目标窗口，模拟按键后安全恢复状态。

---

### Task 1: 项目骨架初始化与 SQLite 数据库服务

**Files:**
- Create: `requirements.txt`
- Create: `src/database.py`
- Test: `tests/test_database.py`

**Interfaces:**
- Produces: `DatabaseManager` 类
  - `init_db(db_path: str = "chat_helper.db") -> None`
  - `get_categories() -> list[dict]`
  - `add_category(name: str, sort_order: int) -> int`
  - `update_category(cat_id: int, name: str, sort_order: int) -> bool`
  - `delete_category(cat_id: int) -> bool`
  - `get_replies(category_id: int | None = None, keyword: str = "") -> list[dict]`
  - `add_reply(category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int) -> int`
  - `update_reply(reply_id: int, category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int) -> bool`
  - `delete_reply(reply_id: int) -> bool`
  - `increment_use_count(reply_id: int) -> bool`
  - `get_setting(key: str, default: str) -> str`
  - `set_setting(key: str, value: str) -> None`
  - `backup_database(backup_path: str) -> bool`
  - `restore_database(restore_path: str) -> bool`

- [ ] **Step 1: 编写失败的数据库单元测试**

```python
# tests/test_database.py
import os
import tempfile
import pytest
from src.database import DatabaseManager

@pytest.fixture
def db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_chat.db")
    manager = DatabaseManager(db_path)
    manager.init_db()
    yield manager
    manager.close()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_category_crud(db):
    cat_id = db.add_category("常见问答", 1)
    assert cat_id > 0
    
    categories = db.get_categories()
    assert len(categories) == 1
    assert categories[0]["name"] == "常见问答"
    assert categories[0]["reply_count"] == 0

    assert db.update_category(cat_id, "常用话术", 2) is True
    updated = db.get_categories()[0]
    assert updated["name"] == "常用话术"
    assert updated["sort_order"] == 2

    assert db.delete_category(cat_id) is True
    assert len(db.get_categories()) == 0

def test_reply_crud_and_search(db):
    cat_id = db.add_category("售后服务", 1)
    attachments = [{"name": "售后指南.pdf", "path": "C:/docs/guide.pdf", "size": 1024}]
    tags = ["退货", "保修"]
    
    reply_id = db.add_reply(cat_id, "退款流程说明", "亲，退款流程如下：1.提交申请 2.审核通过", attachments, tags, 1)
    assert reply_id > 0

    # 验证分类关联与统计
    categories = db.get_categories()
    assert categories[0]["reply_count"] == 1

    # 关键字搜索
    results = db.get_replies(category_id=cat_id, keyword="退款流程")
    assert len(results) == 1
    assert results[0]["title"] == "退款流程说明"
    assert len(results[0]["attachments"]) == 1
    assert results[0]["tags"] == ["退货", "保修"]

    # 使用计数自增
    assert db.increment_use_count(reply_id) is True
    item = db.get_replies(category_id=cat_id)[0]
    assert item["use_count"] == 1

    # 删除
    assert db.delete_reply(reply_id) is True
    assert len(db.get_replies(category_id=cat_id)) == 0
```

- [ ] **Step 2: 运行测试以确认失败**

运行: `pytest tests/test_database.py`  
预期: FAIL (ModuleNotFoundError: No module named 'src.database')

- [ ] **Step 3: 编写 `requirements.txt` 与 `src/database.py` 实现**

```txt
# requirements.txt
pywebview>=5.1
pywin32>=306
pystray>=0.19.5
Pillow>=10.0.0
keyboard>=0.13.5
pytest>=8.0.0
```

```python
# src/database.py
import sqlite3
import json
import shutil
import os
from typing import Any

class DatabaseManager:
    def __init__(self, db_path: str = "chat_helper.db"):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def init_db(self) -> None:
        conn = self.get_connection()
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS quick_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    attachments_json TEXT DEFAULT '[]',
                    tags_json TEXT DEFAULT '[]',
                    sort_order INTEGER DEFAULT 0,
                    use_count INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

    def get_categories(self) -> list[dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.sort_order, COUNT(r.id) as reply_count
            FROM categories c
            LEFT JOIN quick_replies r ON r.category_id = c.id
            GROUP BY c.id, c.name, c.sort_order
            ORDER BY c.sort_order ASC, c.id ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, sort_order: int = 0) -> int:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name, sort_order) VALUES (?, ?)", (name, sort_order))
            return cursor.lastrowid or 0

    def update_category(self, cat_id: int, name: str, sort_order: int) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE categories SET name = ?, sort_order = ? WHERE id = ?", (name, sort_order, cat_id))
            return cursor.rowcount > 0

    def delete_category(self, cat_id: int) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            return cursor.rowcount > 0

    def get_replies(self, category_id: int | None = None, keyword: str = "") -> list[dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM quick_replies WHERE 1=1"
        params: list[Any] = []
        if category_id is not None:
            query += " AND category_id = ?"
            params.append(category_id)
        if keyword:
            query += " AND (title LIKE ? OR content LIKE ? OR tags_json LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        query += " ORDER BY sort_order ASC, id ASC"
        cursor.execute(query, params)
        
        results: list[dict[str, Any]] = []
        for row in cursor.fetchall():
            d = dict(row)
            d["attachments"] = json.loads(d.get("attachments_json") or "[]")
            d["tags"] = json.loads(d.get("tags_json") or "[]")
            results.append(d)
        return results

    def add_reply(self, category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int = 0) -> int:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quick_replies (category_id, title, content, attachments_json, tags_json, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (category_id, title, content, json.dumps(attachments, ensure_ascii=False), json.dumps(tags, ensure_ascii=False), sort_order))
            return cursor.lastrowid or 0

    def update_reply(self, reply_id: int, category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE quick_replies
                SET category_id = ?, title = ?, content = ?, attachments_json = ?, tags_json = ?, sort_order = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (category_id, title, content, json.dumps(attachments, ensure_ascii=False), json.dumps(tags, ensure_ascii=False), sort_order, reply_id))
            return cursor.rowcount > 0

    def delete_reply(self, reply_id: int) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quick_replies WHERE id = ?", (reply_id,))
            return cursor.rowcount > 0

    def increment_use_count(self, reply_id: int) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE quick_replies SET use_count = use_count + 1 WHERE id = ?", (reply_id,))
            return cursor.rowcount > 0

    def get_setting(self, key: str, default: str = "") -> str:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        conn = self.get_connection()
        with conn:
            conn.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))

    def backup_database(self, backup_path: str) -> bool:
        try:
            self.close()
            shutil.copyfile(self.db_path, backup_path)
            return True
        except Exception:
            return False

    def restore_database(self, restore_path: str) -> bool:
        try:
            self.close()
            shutil.copyfile(restore_path, self.db_path)
            self.init_db()
            return True
        except Exception:
            return False

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
```

- [ ] **Step 4: 运行测试确认通过**

运行: `pytest tests/test_database.py -v`  
预期: PASS

---

### Task 2: Win32 剪贴板文件流与智能变量发送引擎

**Files:**
- Create: `src/win32_clipboard.py`
- Create: `src/send_engine.py`
- Test: `tests/test_send_engine.py`

**Interfaces:**
- Produces: `Win32Clipboard` 类
  - `set_text(text: str) -> bool`
  - `set_files(file_paths: list[str]) -> bool`
- Produces: `SendEngine` 类
  - `interpolate_variables(template: str, extra_vars: dict = None) -> str`
  - `send_payload(target_hwnd: int, text: str, attachments: list[dict], mode: str = "normal", delays: dict = None) -> bool`

- [ ] **Step 1: 编写变量插值与发送格式单元测试**

```python
# tests/test_send_engine.py
import datetime
import pytest
from src.send_engine import SendEngine

def test_variable_interpolation():
    engine = SendEngine()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    template = "尊敬的客户您好，今天是{日期}，请查收！"
    result = engine.interpolate_variables(template)
    assert today_str in result
    assert "{日期}" not in result

def test_greeting_interpolation():
    engine = SendEngine()
    result = engine.interpolate_variables("祝您{问候语}，合作愉快！")
    assert any(g in result for g in ["早上好", "上午好", "下午好", "晚上好"])

def test_custom_variables():
    engine = SendEngine()
    template = "你好 {客户名}，您的订单号为 {订单号}"
    result = engine.interpolate_variables(template, {"客户名": "张总", "订单号": "WX123456"})
    assert result == "你好 张总，您的订单号为 WX123456"
```

- [ ] **Step 2: 编写 `src/win32_clipboard.py` 完整实现（`CF_HDROP` 注入）**

```python
# src/win32_clipboard.py
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

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    @classmethod
    def set_text(cls, text: str, max_retries: int = 5) -> bool:
        for _ in range(max_retries):
            if cls.user32.OpenClipboard(None):
                try:
                    cls.user32.EmptyClipboard()
                    encoded = text.encode("utf-16le") + b"\0\0"
                    h_mem = cls.kernel32.GlobalAlloc(cls.GHND, len(encoded))
                    if h_mem:
                        p_mem = cls.kernel32.GlobalLock(h_mem)
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

        for _ in range(max_retries):
            if cls.user32.OpenClipboard(None):
                try:
                    cls.user32.EmptyClipboard()
                    h_mem = cls.kernel32.GlobalAlloc(cls.GHND, total_len)
                    if h_mem:
                        p_mem = cls.kernel32.GlobalLock(h_mem)
                        ctypes.memmove(p_mem, total_bytes, total_len)
                        cls.kernel32.GlobalUnlock(h_mem)
                        cls.user32.SetClipboardData(cls.CF_HDROP, h_mem)
                        return True
                finally:
                    cls.user32.CloseClipboard()
            time.sleep(0.05)
        return False
```

- [ ] **Step 3: 编写 `src/send_engine.py` 实现**

```python
# src/send_engine.py
import time
import datetime
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

        result = template
        for tag, val in mapping.items():
            result = result.replace(tag, val)
        return result

    def _activate_window(self, hwnd: int) -> bool:
        try:
            self.user32.SwitchToThisWindow(hwnd, True)
            self.user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def _simulate_paste(self, delay_ms: int = 100) -> None:
        time.sleep(delay_ms / 1000.0)
        self.user32.keybd_event(self.VK_CONTROL, 0, 0, 0)
        self.user32.keybd_event(self.VK_V, 0, 0, 0)
        self.user32.keybd_event(self.VK_V, 0, self.KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(self.VK_CONTROL, 0, self.KEYEVENTF_KEYUP, 0)

    def _simulate_enter(self, delay_ms: int = 100) -> None:
        time.sleep(delay_ms / 1000.0)
        self.user32.keybd_event(self.VK_RETURN, 0, 0, 0)
        self.user32.keybd_event(self.VK_RETURN, 0, self.KEYEVENTF_KEYUP, 0)

    def send_payload(self, target_hwnd: int, text: str, attachments: list[dict], mode: str = "normal", delays: dict = None) -> bool:
        delays = delays or {"paste_delay": 120, "enter_delay": 120, "char_delay": 150}
        p_delay = delays.get("paste_delay", 120)
        e_delay = delays.get("enter_delay", 120)
        c_delay = delays.get("char_delay", 150)

        interpolated_text = self.interpolate_variables(text)

        if not target_hwnd or not self.user32.IsWindow(target_hwnd):
            return False

        self._activate_window(target_hwnd)

        if mode == "paste_only":
            if interpolated_text:
                Win32Clipboard.set_text(interpolated_text)
                self._simulate_paste(p_delay)
            return True

        if mode == "reverse":
            interpolated_text = interpolated_text[::-1]

        if mode == "typewriter":
            for ch in interpolated_text:
                if ch.strip():
                    Win32Clipboard.set_text(ch)
                    self._simulate_paste(50)
                    self._simulate_enter(50)
                    time.sleep(c_delay / 1000.0)
            return True

        repeat_count = 3 if mode == "repeat3" else 1
        for _ in range(repeat_count):
            if interpolated_text:
                Win32Clipboard.set_text(interpolated_text)
                self._simulate_paste(p_delay)
                self._simulate_enter(e_delay)

            # 顺序发送多附件
            for item in attachments:
                path = item.get("path") if isinstance(item, dict) else str(item)
                if path:
                    Win32Clipboard.set_files([path])
                    self._simulate_paste(p_delay)
                    self._simulate_enter(e_delay)
                    time.sleep(0.15)
        return True
```

- [ ] **Step 4: 运行测试确认通过**

运行: `pytest tests/test_send_engine.py -v`  
预期: PASS

---

### Task 3: Win32 原生吸附与跟随引擎 (`docking_engine.py`)

**Files:**
- Create: `src/docking_engine.py`
- Test: `tests/test_docking_engine.py`

**Interfaces:**
- Produces: `DockingEngine` 类
  - `set_helper_hwnd(hwnd: int) -> None`
  - `start() -> None`
  - `stop() -> None`
  - `toggle_collapse() -> bool`
  - `get_active_target_hwnd() -> int`
  - `update_dock_position(force: bool = False) -> None`

- [ ] **Step 1: 编写吸附计算与窗口过滤测试**

```python
# tests/test_docking_engine.py
from src.docking_engine import DockingEngine, TargetWindowInfo

def test_docking_rect_calculations():
    engine = DockingEngine()
    target_rect = (100, 100, 900, 700)
    
    expanded_pos = engine.calculate_dock_pos(target_rect, collapsed=False, sidebar_width=400)
    assert expanded_pos == (900, 100, 400, 600)

    collapsed_pos = engine.calculate_dock_pos(target_rect, collapsed=True, icon_size=32)
    assert collapsed_pos == (868, 68, 32, 32)
```

- [ ] **Step 2: 编写 `src/docking_engine.py` 实现（Win32 Hook + SetWindowPos）**

```python
# src/docking_engine.py
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
            ctypes.windll.kernel32.QueryFullProcessImageNameW(h_proc, 0, name_buff, ctypes.byref(size))
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
```

- [ ] **Step 3: 运行测试确认通过**

运行: `pytest tests/test_docking_engine.py -v`  
预期: PASS

---

### Task 4: pywebview RPC 桥接与主程序装配 (`src/api.py`, `src/main.py`)

**Files:**
- Create: `src/api.py`
- Create: `src/main.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Produces: `JsApi` 类
  - 暴露 `getCategories()`, `saveCategory(data)`, `deleteCategory(id)`
  - 暴露 `getReplies(categoryId, keyword)`, `saveReply(data)`, `deleteReply(id)`
  - 暴露 `sendReply(replyId, mode)`
  - 暴露 `toggleCollapse()`, `minimizeWindow()`, `closeApp()`
  - 暴露 `selectFiles()`, `getSettings()`, `saveSetting(key, val)`, `backupDb()`, `restoreDb()`

- [ ] **Step 1: 编写 API 桥接层逻辑测试**

```python
# tests/test_api.py
import pytest
from unittest.mock import MagicMock
from src.api import JsApi

def test_api_calls_database():
    mock_db = MagicMock()
    mock_db.get_categories.return_value = [{"id": 1, "name": "售后", "reply_count": 0}]
    mock_dock = MagicMock()
    mock_send = MagicMock()
    
    api = JsApi(mock_db, mock_dock, mock_send)
    cats = api.getCategories()
    assert len(cats) == 1
    assert cats[0]["name"] == "售后"
```

- [ ] **Step 2: 编写 `src/api.py` 实现**

```python
# src/api.py
import webview
from typing import Any
from src.database import DatabaseManager
from src.docking_engine import DockingEngine
from src.send_engine import SendEngine

class JsApi:
    def __init__(self, db: DatabaseManager, dock: DockingEngine, send: SendEngine):
        self.db = db
        self.dock = dock
        self.send = send
        self._window: webview.Window | None = None

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def getCategories(self) -> list[dict[str, Any]]:
        return self.db.get_categories()

    def saveCategory(self, data: dict[str, Any]) -> dict[str, Any]:
        cat_id = data.get("id")
        name = data.get("name", "").strip()
        order = int(data.get("sort_order", 0))
        if not name:
            return {"success": False, "error": "分类名称不能为空"}
        if cat_id:
            ok = self.db.update_category(cat_id, name, order)
            return {"success": ok}
        else:
            new_id = self.db.add_category(name, order)
            return {"success": new_id > 0, "id": new_id}

    def deleteCategory(self, cat_id: int) -> dict[str, Any]:
        return {"success": self.db.delete_category(cat_id)}

    def getReplies(self, category_id: int | None = None, keyword: str = "") -> list[dict[str, Any]]:
        return self.db.get_replies(category_id=category_id, keyword=keyword)

    def saveReply(self, data: dict[str, Any]) -> dict[str, Any]:
        reply_id = data.get("id")
        cat_id = int(data.get("category_id", 0))
        title = data.get("title", "").strip()
        content = data.get("content", "")
        attachments = data.get("attachments", [])
        tags = data.get("tags", [])
        order = int(data.get("sort_order", 0))

        if not title:
            return {"success": False, "error": "标题不能为空"}

        if reply_id:
            ok = self.db.update_reply(reply_id, cat_id, title, content, attachments, tags, order)
            return {"success": ok}
        else:
            new_id = self.db.add_reply(cat_id, title, content, attachments, tags, order)
            return {"success": new_id > 0, "id": new_id}

    def deleteReply(self, reply_id: int) -> dict[str, Any]:
        return {"success": self.db.delete_reply(reply_id)}

    def sendReply(self, reply_id: int, mode: str = "normal") -> dict[str, Any]:
        replies = self.db.get_replies()
        target_reply = next((r for r in replies if r["id"] == reply_id), None)
        if not target_reply:
            return {"success": False, "error": "话术不存在"}

        target_hwnd = self.dock.current_target_hwnd
        if not target_hwnd:
            return {"success": False, "error": "未检测到已激活的目标聊天窗口"}

        ok = self.send.send_payload(
            target_hwnd=target_hwnd,
            text=target_reply["content"],
            attachments=target_reply["attachments"],
            mode=mode
        )
        if ok:
            self.db.increment_use_count(reply_id)
        return {"success": ok}

    def selectFiles(self) -> list[str]:
        if not self._window:
            return []
        result = self._window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True)
        return list(result) if result else []

    def toggleCollapse(self) -> bool:
        return self.dock.toggle_collapse()

    def getSettings(self) -> dict[str, str]:
        return {
            "dark_mode": self.db.get_setting("dark_mode", "0"),
            "hotkey": self.db.get_setting("hotkey", "alt+space"),
            "paste_delay": self.db.get_setting("paste_delay", "120"),
            "enter_delay": self.db.get_setting("enter_delay", "120"),
        }

    def saveSetting(self, key: str, val: str) -> None:
        self.db.set_setting(key, str(val))
```

- [ ] **Step 3: 编写主入口 `src/main.py`**

```python
# src/main.py
import os
import sys
import webview
import ctypes
from src.database import DatabaseManager
from src.send_engine import SendEngine
from src.docking_engine import DockingEngine
from src.api import JsApi

def create_app():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "ChatHelper_Python_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(0, "聊天助手已经在运行中！", "提示", 0x40)
        sys.exit(0)

    db = DatabaseManager("chat_helper.db")
    db.init_db()
    send = SendEngine()
    dock = DockingEngine(sidebar_width=408)
    api = JsApi(db, dock, send)

    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
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

    def on_loaded():
        hwnd = ctypes.windll.user32.FindWindowW(None, "微信聊天助手")
        if hwnd:
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000080)
            dock.set_helper_hwnd(hwnd)
            dock.start()

    window.events.loaded += on_loaded
    webview.start(debug=False)

if __name__ == "__main__":
    create_app()
```

- [ ] **Step 4: 运行测试确认通过**

运行: `pytest tests/test_api.py -v`  
预期: PASS

---

### Task 5: Vue 3 + Vite 前端工程初始化与毛玻璃主界面

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/assets/main.css`
- Create: `frontend/src/components/HeaderBar.vue`
- Create: `frontend/src/components/CategoryNav.vue`

- [ ] **Step 1: 编写 `frontend/package.json` 与 `frontend/vite.config.js`**

```json
{
  "name": "chathelper-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "lucide-vue-next": "^0.344.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.1.0"
  }
}
```

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true
  },
  server: {
    port: 5173
  }
})
```

- [ ] **Step 2: 编写现代化毛玻璃与暗黑样式 `frontend/src/assets/main.css`**

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-primary: rgba(255, 255, 255, 0.85);
  --bg-secondary: rgba(245, 247, 250, 0.9);
  --bg-card: rgba(255, 255, 255, 0.95);
  --border-color: rgba(226, 232, 240, 0.8);
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --accent-color: #07c160;
  --accent-hover: #06ad56;
  --accent-light: rgba(7, 193, 96, 0.12);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
}

.dark {
  --bg-primary: rgba(18, 22, 28, 0.88);
  --bg-secondary: rgba(26, 32, 44, 0.92);
  --bg-card: rgba(30, 41, 59, 0.85);
  --border-color: rgba(51, 65, 85, 0.7);
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --accent-color: #07c160;
  --accent-hover: #10d66e;
  --accent-light: rgba(7, 193, 96, 0.2);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  user-select: none;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

body {
  background: var(--bg-primary);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: var(--text-primary);
  overflow: hidden;
  height: 100vh;
  border-left: 1px solid var(--border-color);
}
```

---

### Task 6: 话术卡片流、即时搜索与多模式发送组件

**Files:**
- Create: `frontend/src/components/SearchBar.vue`
- Create: `frontend/src/components/ReplyCardList.vue`
- Create: `frontend/src/components/ReplyCard.vue`
- Create: `frontend/src/components/ReplyEditModal.vue`

- [ ] **Step 1: 编写搜索栏组件 `SearchBar.vue`**

```vue
<!-- frontend/src/components/SearchBar.vue -->
<template>
  <div class="search-container">
    <Search :size="15" class="search-icon" />
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      placeholder="搜索话术/标签/正文 (快捷键 Alt+Space)"
      class="search-input"
    />
    <button v-if="modelValue" @click="$emit('update:modelValue', '')" class="clear-btn"><X :size="14" /></button>
    <button @click="$emit('create-reply')" class="add-btn" title="新增话术"><Plus :size="16" /></button>
  </div>
</template>

<script setup>
import { Search, X, Plus } from 'lucide-vue-next'
defineProps({ modelValue: String })
defineEmits(['update:modelValue', 'create-reply'])
</script>
```

- [ ] **Step 2: 编写话术卡片与多模式发送 `ReplyCard.vue`**

```vue
<!-- frontend/src/components/ReplyCard.vue -->
<template>
  <div class="reply-card" @dblclick="$emit('send', reply.id, 'paste_only')">
    <div class="card-header">
      <span class="card-title">{{ reply.title }}</span>
      <span class="use-badge" v-if="reply.use_count > 0">{{ reply.use_count }}次</span>
    </div>
    <div class="card-content">{{ reply.content }}</div>
    <div class="card-footer">
      <div class="attachments" v-if="reply.attachments && reply.attachments.length">
        <span v-for="(att, idx) in reply.attachments" :key="idx" class="att-chip">
          📎 {{ att.name || '附件' }}
        </span>
      </div>
      <div class="card-actions">
        <button class="send-btn" @click.stop="$emit('send', reply.id, 'normal')">发送</button>
        <button class="more-btn" @click.stop="showMenu = !showMenu">⋮</button>
        <div class="dropdown-menu" v-if="showMenu" @click.stop>
          <div class="menu-item" @click="emitMode('typewriter')">逐字慢发 (打字机)</div>
          <div class="menu-item" @click="emitMode('repeat3')">连发3次</div>
          <div class="menu-item" @click="emitMode('reverse')">倒序发送</div>
          <div class="menu-item" @click="emitMode('paste_only')">仅粘贴不回车</div>
          <hr class="menu-divider" />
          <div class="menu-item" @click="$emit('edit', reply)">编辑话术</div>
          <div class="menu-item delete" @click="$emit('delete', reply.id)">删除</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ reply: Object })
const emit = defineEmits(['send', 'edit', 'delete'])
const showMenu = ref(false)

function emitMode(mode) {
  showMenu.value = false
  emit('send', props.reply.id, mode)
}
</script>
```

---

### Task 7: 设置面板、数据库备份/还原与托盘管理

**Files:**
- Create: `frontend/src/components/SettingsModal.vue`
- Create: `src/tray_manager.py`

- [ ] **Step 1: 编写系统托盘管理模块 `src/tray_manager.py`**

```python
# src/tray_manager.py
import pystray
from PIL import Image, ImageDraw
import threading

def create_default_icon():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=(7, 193, 96, 255))
    draw.text((18, 16), "WX", fill="white")
    return image

class TrayManager:
    def __init__(self, on_toggle, on_exit):
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.icon = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("显示/隐藏助手", self.on_toggle, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.on_exit)
        )
        self.icon = pystray.Icon("ChatHelper", create_default_icon(), "微信聊天助手", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()
```

---

### Task 8: 前端构建整合与 PyInstaller 绿色免安装打包

**Files:**
- Create: `build_app.py`
- Test: 冒烟测试打包后的可执行文件

- [ ] **Step 1: 编写自动化构建脚本 `build_app.py`**

```python
# build_app.py
import os
import subprocess
import shutil

def build():
    print("[1/3] 构建 Vue 3 前端静态资源...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    subprocess.run("npm run build", shell=True, cwd=frontend_dir, check=True)

    print("[2/3] 检查生成的前端静态产物...")
    dist_dir = os.path.join(frontend_dir, "dist")
    if not os.path.exists(os.path.join(dist_dir, "index.html")):
        raise FileNotFoundError("前端构建产物未找到！")

    print("[3/3] 运行 PyInstaller 生成便携绿色包...")
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onedir",
        "--name=ChatHelper",
        f"--add-data={dist_dir};frontend/dist",
        "--clean",
        "-y",
        "src/main.py"
    ]
    subprocess.run(cmd, check=True)
    print("打包成功！输出路径：dist/ChatHelper/ChatHelper.exe")

if __name__ == "__main__":
    build()
```

- [ ] **Step 2: 验证全量打包与冒烟测试**

运行: `python build_app.py`  
验证内容:
1. 启动 `dist/ChatHelper/ChatHelper.exe` 验证无控制台黑框；
2. 激活 PC 微信，验证窗口自动 0 延迟贴边展开；
3. 点击话术卡片，验证剪贴板注入并自动发送文本与多附件；
4. 点击托盘图标，验证正常唤出与退出。
