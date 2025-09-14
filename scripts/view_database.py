#!/usr/bin/env python3
"""
Script to view database contents
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.database import init_database
from src.models import WordRecord, db


def view_database():
    """Display all records in the database"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        records = WordRecord.query.all()

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
            print(f"創建時間: {record.created_on}")
            print(f"更新時間: {record.updated_on}")
            print(f"定義: {record.definition[:100]}...")  # 只顯示前100字
            print("-" * 80)


def count_records():
    """Count records by language"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        english_count = WordRecord.query.filter_by(language="english").count()
        chinese_count = WordRecord.query.filter_by(language="chinese").count()
        total_queries = (
            db.session.query(db.func.sum(WordRecord.query_times)).scalar() or 0
        )

        print(f"英文單字: {english_count} 筆")
        print(f"中文單字: {chinese_count} 筆")
        print(f"總查詢次數: {total_queries} 次")


if __name__ == "__main__":
    print("查看資料庫內容")
    print("=" * 40)
    count_records()
    print()
    view_database()
