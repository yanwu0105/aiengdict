"""
Database configuration and utilities
"""

import os
from datetime import datetime, timezone
from flask import Flask
from src.models import db, WordRecord, User


def init_database(app: Flask):
    """Initialize database with Flask app"""
    # Check if we're in testing mode
    if os.getenv("TESTING") or os.getenv("FLASK_ENV") == "testing":
        # Use in-memory database for testing
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "sqlite:///:memory:"
        )
        app.config["TESTING"] = True
    else:
        # Configure SQLite database for production
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_path = os.path.join(basedir, "..", "dictionary.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()


def save_word_record(
    word: str, language: str, definition: str, user_id: int = None
) -> bool:
    """
    Save or update word record in database

    Args:
        word: The queried word
        language: 'chinese' or 'english'
        definition: AI response definition
        user_id: Optional user ID for authenticated users

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        record = WordRecord.find_or_create(word, language, definition, user_id)
        db.session.add(record)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Database save error: {e}")
        return False


def get_query_history(limit: int = 20, user_id: int = None) -> list:
    """
    Get query history ordered by query times (descending)

    Args:
        limit: Maximum number of records to return
        user_id: Optional user ID to filter records for authenticated users

    Returns:
        list: List of dictionaries containing word history data
    """
    try:
        query = WordRecord.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        else:
            # For anonymous users, only show records without user_id
            query = query.filter_by(user_id=None)

        records = query.order_by(WordRecord.query_times.desc()).limit(limit).all()
        return [
            {
                "word": record.word,
                "language": record.language,
                "query_times": record.query_times,
                "definition": record.definition[:200] + "..."
                if len(record.definition) > 200
                else record.definition,
                "updated_on": record.updated_on.strftime("%Y-%m-%d %H:%M"),
            }
            for record in records
        ]
    except Exception as e:
        print(f"Database query error: {e}")
        return []


def create_user(
    username: str, email: str, password: str, display_name: str = None
) -> tuple[bool, str]:
    """
    Create a new user

    Args:
        username: Unique username
        email: Unique email address
        password: Plain text password (will be hashed)
        display_name: Optional display name

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if username already exists
        if User.find_by_username(username):
            return False, "用戶名已存在"

        # Check if email already exists
        if User.find_by_email(email):
            return False, "電子郵件已被註冊"

        # Create new user
        user = User(username=username, email=email, display_name=display_name)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return True, "註冊成功"

    except Exception as e:
        db.session.rollback()
        print(f"User creation error: {e}")
        return False, "註冊失敗，請稍後再試"


def authenticate_user(username: str, password: str) -> tuple[User | None, str]:
    """
    Authenticate user login

    Args:
        username: Username or email
        password: Plain text password

    Returns:
        tuple: (user: User | None, message: str)
    """
    try:
        # Try to find user by username or email
        user = User.find_by_username(username)
        if not user:
            user = User.find_by_email(username)

        if not user:
            return None, "用戶不存在"

        if not user.check_password(password):
            return None, "密碼錯誤"

        if not user.is_active:
            return None, "帳戶已被停用"

        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        return user, "登入成功"

    except Exception as e:
        print(f"Authentication error: {e}")
        return None, "登入失敗，請稍後再試"
