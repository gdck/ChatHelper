import os
import json
import shutil
import threading
from typing import Any

class JsonStorageManager:
    """
    轻量化纯 JSON 数据存储管理器
    存储路径：%APPDATA%\\ChatHelper\\data.json
    采用线程锁与原子写入（临时文件写入+安全重命名替换），保证高并发读写零损坏
    """
    def __init__(self, custom_path: str | None = None):
        if custom_path:
            self.data_path = os.path.abspath(custom_path)
        else:
            appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
            self.data_dir = os.path.join(appdata, "ChatHelper")
            os.makedirs(self.data_dir, exist_ok=True)
            self.data_path = os.path.join(self.data_dir, "data.json")

        self._lock = threading.RLock()
        self._data: dict[str, Any] = {
            "categories": [],
            "quick_replies": [],
            "app_settings": {
                "dark_mode": "0",
                "hotkey": "alt+space",
                "paste_delay": "120",
                "enter_delay": "120",
                "typewriter_delay": "500",
                "repeat_delay": "500"
            }
        }
        self.init_storage()

    def _get_next_id(self, items: list[dict[str, Any]]) -> int:
        if not items:
            return 1
        return max(item.get("id", 0) for item in items) + 1

    def init_storage(self) -> None:
        with self._lock:
            if os.path.exists(self.data_path):
                try:
                    with open(self.data_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                        if isinstance(loaded, dict):
                            self._data["categories"] = loaded.get("categories", [])
                            self._data["quick_replies"] = loaded.get("quick_replies", [])
                            self._data["app_settings"] = {**self._data["app_settings"], **loaded.get("app_settings", {})}
                            return
                except Exception:
                    pass

            # 首次初始化时注入优质示例分类与默认话术
            self._data["categories"] = [
                {"id": 1, "name": "常用问候", "sort_order": 1},
                {"id": 2, "name": "售后服务", "sort_order": 2},
                {"id": 3, "name": "产品与报价", "sort_order": 3},
            ]
            self._data["quick_replies"] = [
                {
                    "id": 1,
                    "category_id": 1,
                    "title": "问候与介绍",
                    "content": "您好！祝您{问候语}，很高兴为您服务。今天是{日期}，请问有什么可以帮您？",
                    "attachments": [],
                    "tags": ["高频", "问候"],
                    "sort_order": 1,
                    "use_count": 12
                },
                {
                    "id": 2,
                    "category_id": 2,
                    "title": "7天退换货政策",
                    "content": "亲，我们支持7天无理由退换货。请保持包装完好，我们将安排快递上门取件。",
                    "attachments": [],
                    "tags": ["售后", "政策"],
                    "sort_order": 1,
                    "use_count": 8
                },
                {
                    "id": 3,
                    "category_id": 3,
                    "title": "产品画册与报价单",
                    "content": "您好，这是我们最新的产品画册与详细报价单，请您查阅。如有任何疑问随时联系我！",
                    "attachments": [],
                    "tags": ["资料", "报价"],
                    "sort_order": 1,
                    "use_count": 5
                }
            ]
            self._save()

    def _save(self) -> None:
        """原子写入，避免意外断电/中断导致文件损坏"""
        temp_path = self.data_path + ".tmp"
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        if os.path.exists(self.data_path):
            os.replace(temp_path, self.data_path)
        else:
            os.rename(temp_path, self.data_path)

    # 兼容原 DatabaseManager 的接口
    def init_db(self) -> None:
        self.init_storage()

    def get_categories(self) -> list[dict[str, Any]]:
        with self._lock:
            cats = sorted(self._data["categories"], key=lambda c: (c.get("sort_order", 0), c.get("id", 0)))
            results = []
            for c in cats:
                cat_id = c["id"]
                count = sum(1 for r in self._data["quick_replies"] if r.get("category_id") == cat_id)
                results.append({
                    "id": cat_id,
                    "name": c["name"],
                    "sort_order": c.get("sort_order", 0),
                    "reply_count": count
                })
            return results

    def add_category(self, name: str, sort_order: int = 0) -> int:
        with self._lock:
            new_id = self._get_next_id(self._data["categories"])
            self._data["categories"].append({
                "id": new_id,
                "name": name,
                "sort_order": sort_order
            })
            self._save()
            return new_id

    def update_category(self, cat_id: int, name: str, sort_order: int) -> bool:
        with self._lock:
            for c in self._data["categories"]:
                if c["id"] == cat_id:
                    c["name"] = name
                    c["sort_order"] = sort_order
                    self._save()
                    return True
            return False

    def delete_category(self, cat_id: int) -> bool:
        with self._lock:
            initial_len = len(self._data["categories"])
            self._data["categories"] = [c for c in self._data["categories"] if c["id"] != cat_id]
            # 级联删除属于该分类的话术
            self._data["quick_replies"] = [r for r in self._data["quick_replies"] if r.get("category_id") != cat_id]
            if len(self._data["categories"]) < initial_len:
                self._save()
                return True
            return False

    def get_replies(self, category_id: int | None = None, keyword: str = "") -> list[dict[str, Any]]:
        with self._lock:
            filtered = list(self._data["quick_replies"])
            if category_id is not None:
                filtered = [r for r in filtered if r.get("category_id") == category_id]
            if keyword:
                kw = keyword.lower()
                def match(r):
                    t = r.get("title", "").lower()
                    c = r.get("content", "").lower()
                    tags = " ".join(r.get("tags", [])).lower()
                    return kw in t or kw in c or kw in tags
                filtered = [r for r in filtered if match(r)]

            filtered.sort(key=lambda r: (r.get("sort_order", 0), r.get("id", 0)))
            # 保证结构一致性
            res = []
            for r in filtered:
                res.append({
                    "id": r["id"],
                    "category_id": r.get("category_id", 0),
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "attachments": r.get("attachments", []),
                    "tags": r.get("tags", []),
                    "sort_order": r.get("sort_order", 0),
                    "use_count": r.get("use_count", 0)
                })
            return res

    def add_reply(self, category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int = 0) -> int:
        with self._lock:
            new_id = self._get_next_id(self._data["quick_replies"])
            self._data["quick_replies"].append({
                "id": new_id,
                "category_id": category_id,
                "title": title,
                "content": content,
                "attachments": attachments or [],
                "tags": tags or [],
                "sort_order": sort_order,
                "use_count": 0
            })
            self._save()
            return new_id

    def update_reply(self, reply_id: int, category_id: int, title: str, content: str, attachments: list[dict], tags: list[str], sort_order: int) -> bool:
        with self._lock:
            for r in self._data["quick_replies"]:
                if r["id"] == reply_id:
                    r["category_id"] = category_id
                    r["title"] = title
                    r["content"] = content
                    r["attachments"] = attachments or []
                    r["tags"] = tags or []
                    r["sort_order"] = sort_order
                    self._save()
                    return True
            return False

    def delete_reply(self, reply_id: int) -> bool:
        with self._lock:
            initial_len = len(self._data["quick_replies"])
            self._data["quick_replies"] = [r for r in self._data["quick_replies"] if r["id"] != reply_id]
            if len(self._data["quick_replies"]) < initial_len:
                self._save()
                return True
            return False

    def increment_use_count(self, reply_id: int) -> bool:
        with self._lock:
            for r in self._data["quick_replies"]:
                if r["id"] == reply_id:
                    r["use_count"] = r.get("use_count", 0) + 1
                    self._save()
                    return True
            return False

    def get_setting(self, key: str, default: str = "") -> str:
        with self._lock:
            return str(self._data["app_settings"].get(key, default))

    def set_setting(self, key: str, value: str) -> None:
        with self._lock:
            self._data["app_settings"][key] = str(value)
            self._save()

    def backup_database(self, backup_path: str) -> bool:
        with self._lock:
            try:
                shutil.copyfile(self.data_path, backup_path)
                return True
            except Exception:
                return False

    def restore_database(self, restore_path: str) -> bool:
        with self._lock:
            try:
                shutil.copyfile(restore_path, self.data_path)
                self.init_storage()
                return True
            except Exception:
                return False

    def close(self) -> None:
        pass
