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
        try:
            os.remove(db_path)
        except OSError:
            pass

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

def test_settings_and_backup(db):
    db.set_setting("theme", "dark")
    assert db.get_setting("theme") == "dark"
    assert db.get_setting("non_exist", "default_val") == "default_val"

    temp_dir = tempfile.mkdtemp()
    backup_file = os.path.join(temp_dir, "backup.db")
    assert db.backup_database(backup_file) is True
    assert os.path.exists(backup_file)
    assert db.restore_database(backup_file) is True
