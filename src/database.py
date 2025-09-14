"""
Database configuration and utilities
"""

import os
from flask import Flask
from src.models import db, WordRecord


def init_database(app: Flask):
    """Initialize database with Flask app"""
    # Configure SQLite database
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
