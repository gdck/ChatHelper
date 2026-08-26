import webview
import threading
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

        delays = {
            "paste_delay": int(self.db.get_setting("paste_delay", "120")),
            "enter_delay": int(self.db.get_setting("enter_delay", "120")),
            "typewriter_delay": int(self.db.get_setting("typewriter_delay", "500")),
            "repeat_delay": int(self.db.get_setting("repeat_delay", "500")),
        }

        # 异步线程执行实际按键发送，防止长时间逐字慢发阻塞 pywebview JS 通信通道导致程序死锁闪退
        def async_worker():
            try:
                self.send.send_payload(
                    target_hwnd=target_hwnd,
                    text=target_reply["content"],
                    attachments=target_reply.get("attachments", []),
                    mode=mode,
                    delays=delays
                )
                self.db.increment_use_count(reply_id)
            except Exception as e:
                print(f"[SendEngine] 发送执行异常: {e}")

        threading.Thread(target=async_worker, daemon=True).start()
        return {"success": True}

    def selectFiles(self) -> list[str]:
        if not self._window:
            return []
        try:
            result = self._window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True)
            return list(result) if result else []
        except Exception:
            return []

    def toggleCollapse(self) -> bool:
        state = self.dock.toggle_collapse()
        if self._window:
            try:
                self._window.evaluate_js(f"window.dispatchEvent(new CustomEvent('collapse-changed', {{ detail: {str(state).lower()} }}))")
            except Exception:
                pass
        return state

    def getCollapseState(self) -> bool:
        return self.dock.collapsed

    def getSettings(self) -> dict[str, str]:
        return {
            "dark_mode": self.db.get_setting("dark_mode", "0"),
            "hotkey": self.db.get_setting("hotkey", "alt+space"),
            "paste_delay": self.db.get_setting("paste_delay", "120"),
            "enter_delay": self.db.get_setting("enter_delay", "120"),
            "typewriter_delay": self.db.get_setting("typewriter_delay", "500"),
            "repeat_delay": self.db.get_setting("repeat_delay", "500"),
        }

    def saveSetting(self, key: str, val: str) -> None:
        self.db.set_setting(key, str(val))

    def backupDatabase(self, path: str) -> bool:
        return self.db.backup_database(path)

    def restoreDatabase(self, path: str) -> bool:
        return self.db.restore_database(path)
