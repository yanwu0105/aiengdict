#!/usr/bin/env python3
"""
Database migration script to update schema for user authentication
"""

import sys
import os
import sqlite3
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.database import init_database
from src.models import db


def check_database_schema():
    """Check current database schema"""
    db_path = Path(__file__).parent.parent / "dictionary.db"

    if not db_path.exists():
        print("數據庫文件不存在，將創建新的數據庫。")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_table_exists = cursor.fetchone() is not None

    # Check if word_records has user_id column
    cursor.execute("PRAGMA table_info(word_records)")
    columns = [column[1] for column in cursor.fetchall()]
    user_id_exists = "user_id" in columns

    conn.close()

    print(f"用戶表存在: {'是' if users_table_exists else '否'}")
    print(f"word_records有user_id欄位: {'是' if user_id_exists else '否'}")

    return users_table_exists and user_id_exists


def migrate_database():
    """Migrate database to new schema"""
    db_path = Path(__file__).parent.parent / "dictionary.db"

    if not db_path.exists():
        print("數據庫文件不存在，創建新數據庫...")
        create_new_database()
        return

    print("開始遷移數據庫...")

    # Backup existing data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing records
    try:
        cursor.execute("SELECT * FROM word_records")
        existing_records = cursor.fetchall()
        print(f"找到 {len(existing_records)} 筆現有記錄")

        # Get column names
        cursor.execute("PRAGMA table_info(word_records)")
        old_columns = [column[1] for column in cursor.fetchall()]

    except sqlite3.OperationalError as e:
        print(f"讀取現有數據時出錯: {e}")
        existing_records = []
        old_columns = []

    conn.close()

    # Create backup
    backup_path = db_path.with_suffix(".backup")
    if db_path.exists():
        import shutil

        shutil.copy2(db_path, backup_path)
        print(f"已備份原數據庫到: {backup_path}")

    # Remove old database
    db_path.unlink()

    # Create new database with updated schema
    create_new_database()

    # Restore data if exists
    if existing_records and "user_id" not in old_columns:
        print("正在遷移現有數據...")
        restore_data(existing_records, old_columns)

    print("數據庫遷移完成！")


def create_new_database():
    """Create new database with current schema"""
    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        db.create_all()
        print("已創建新的數據庫架構")


def restore_data(records, old_columns):
    """Restore data to new database"""
    from datetime import datetime

    app = Flask(__name__)
    init_database(app)

    with app.app_context():
        from src.models import WordRecord

        for record in records:
            # Map old record to new structure
            record_dict = dict(zip(old_columns, record))

            # Handle datetime conversion
            created_on = record_dict.get("created_on")
            updated_on = record_dict.get("updated_on")

            if isinstance(created_on, str):
                try:
                    created_on = datetime.fromisoformat(created_on)
                except (ValueError, TypeError):
                    created_on = datetime.now()

            if isinstance(updated_on, str):
                try:
                    updated_on = datetime.fromisoformat(updated_on)
                except (ValueError, TypeError):
                    updated_on = datetime.now()

            new_record = WordRecord(
                word=record_dict.get("word"),
                language=record_dict.get("language"),
                definition=record_dict.get("definition"),
                query_times=record_dict.get("query_times", 1),
                user_id=None,  # Set to None for migrated records (anonymous)
                created_on=created_on,
                updated_on=updated_on,
            )

            db.session.add(new_record)

        try:
            db.session.commit()
            print(f"成功恢復 {len(records)} 筆記錄")
        except Exception as e:
            db.session.rollback()
            print(f"恢復數據時出錯: {e}")


def main():
    """Main migration function"""
    print("AI字典數據庫遷移工具")
    print("=" * 40)

    if check_database_schema():
        print("數據庫架構已是最新版本，無需遷移。")
        return

    print("\n數據庫需要更新以支持用戶認證功能。")
    response = input("是否要開始遷移？(y/N): ").lower().strip()

    if response in ["y", "yes"]:
        migrate_database()
    else:
        print("遷移已取消。")
        print("注意：在遷移之前，某些功能可能無法正常工作。")


if __name__ == "__main__":
    main()
