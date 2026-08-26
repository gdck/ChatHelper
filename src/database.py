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
