#!/usr/bin/env python3
"""
Script to clear database contents
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.database import init_database
from src.models import WordRecord, db


def clear_database():
    """Clear all records from the database"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        # Count records before deletion
        total_records = WordRecord.query.count()

        if total_records == 0:
            print("資料庫已經是空的，沒有資料需要清除")
            return

        print(f"資料庫中共有 {total_records} 筆記錄")

        # Ask for confirmation
        confirm = input("確定要清空所有資料嗎？(y/N): ").strip().lower()

        if confirm not in ["y", "yes", "是"]:
            print("取消清空資料庫操作")
            return

        try:
            # Delete all records
            deleted_count = WordRecord.query.delete()
            db.session.commit()

            print(f"✅ 成功清除 {deleted_count} 筆記錄")
            print("資料庫已清空")

        except Exception as e:
            db.session.rollback()
            print(f"❌ 清空資料庫時發生錯誤: {e}")


def force_clear_database():
    """Force clear database without confirmation (for scripts)"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        try:
            deleted_count = WordRecord.query.delete()
            db.session.commit()
            print(f"✅ 強制清除 {deleted_count} 筆記錄")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ 清空資料庫時發生錯誤: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        force_clear_database()
    else:
        clear_database()
