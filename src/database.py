"""
Database configuration and utilities
"""

import os
from flask import Flask
from src.models import db, WordRecord


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


def save_word_record(word: str, language: str, definition: str) -> bool:
    """
    Save or update word record in database

    Args:
        word: The queried word
        language: 'chinese' or 'english'
        definition: AI response definition

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        record = WordRecord.find_or_create(word, language, definition)
        db.session.add(record)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Database save error: {e}")
        return False


def get_query_history(limit: int = 20) -> list:
    """
    Get query history ordered by query times (descending)

    Args:
        limit: Maximum number of records to return

    Returns:
        list: List of dictionaries containing word history data
    """
    try:
        records = (
            WordRecord.query.order_by(WordRecord.query_times.desc()).limit(limit).all()
        )
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
