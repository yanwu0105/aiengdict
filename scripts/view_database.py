#!/usr/bin/env python3
"""
Script to view database contents
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.database import init_database
from src.models import WordRecord, User, db


def view_database():
    """Display all records in the database"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        try:
            records = WordRecord.query.all()
        except Exception as e:
            print(f"數據庫查詢錯誤: {e}")
            print("這可能是因為數據庫架構需要更新。")
            print("請嘗試運行 'make clear-db-force' 來重置數據庫。")
            return

        if not records:
            print("資料庫中沒有資料")
            return

        print(f"資料庫中共有 {len(records)} 筆記錄：")
        print("=" * 80)

        for record in records:
            print(f"ID: {record.id}")
            print(f"單字: {record.word}")
            print(f"語言: {record.language}")
            print(f"查詢次數: {record.query_times}")

            # Check if user_id column exists
            if hasattr(record, "user_id") and record.user_id:
                user = db.session.get(User, record.user_id)
                print(f"用戶: {user.username if user else '未知用戶'}")
            else:
                print("用戶: 匿名")

            print(f"創建時間: {record.created_on}")
            print(f"更新時間: {record.updated_on}")
            print(f"定義: {record.definition[:100]}...")  # 只顯示前100字
            print("-" * 80)


def count_records():
    """Count records by language"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        try:
            english_count = WordRecord.query.filter_by(language="english").count()
            chinese_count = WordRecord.query.filter_by(language="chinese").count()
            total_queries = (
                db.session.query(db.func.sum(WordRecord.query_times)).scalar() or 0
            )

            print(f"英文單字: {english_count} 筆")
            print(f"中文單字: {chinese_count} 筆")
            print(f"總查詢次數: {total_queries} 次")

            # Show user count if users table exists
            try:
                user_count = User.query.count()
                print(f"註冊用戶: {user_count} 人")
            except Exception:
                print("用戶功能: 尚未啟用")

        except Exception as e:
            print(f"數據庫統計錯誤: {e}")
            print("數據庫架構可能需要更新。")


if __name__ == "__main__":
    print("查看資料庫內容")
    print("=" * 40)
    count_records()
    print()
    view_database()
