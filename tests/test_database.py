"""
Test database functionality
"""

import pytest
import os
import tempfile
from flask import Flask
from src.database import save_word_record
from src.models import db, WordRecord


@pytest.fixture
def app():
    """Create test Flask app with temporary database"""
    app = Flask(__name__)

    # Use temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


def test_save_word_record_new(app):
    """Test saving a new word record"""
    with app.app_context():
        result = save_word_record("hello", "english", "A greeting word")
        assert result is True

        # Check if record was saved
        record = WordRecord.query.filter_by(word="hello", language="english").first()
        assert record is not None
        assert record.word == "hello"
        assert record.language == "english"
        assert record.definition == "A greeting word"
        assert record.query_times == 1


def test_save_word_record_update_existing(app):
    """Test updating an existing word record"""
    with app.app_context():
        # Save first time
        save_word_record("hello", "english", "A greeting word")

        # Save again with different definition
        save_word_record("hello", "english", "Updated greeting word")

        # Should have only one record with updated info
        records = WordRecord.query.filter_by(word="hello", language="english").all()
        assert len(records) == 1

        record = records[0]
        assert record.definition == "Updated greeting word"
        assert record.query_times == 2


def test_save_different_languages(app):
    """Test saving same word in different languages"""
    with app.app_context():
        save_word_record("hello", "english", "English greeting")
        save_word_record("hello", "chinese", "Chinese meaning")

        # Should have two separate records
        english_record = WordRecord.query.filter_by(
            word="hello", language="english"
        ).first()
        chinese_record = WordRecord.query.filter_by(
            word="hello", language="chinese"
        ).first()

        assert english_record is not None
        assert chinese_record is not None
        assert english_record.definition == "English greeting"
        assert chinese_record.definition == "Chinese meaning"


def test_word_record_find_or_create(app):
    """Test WordRecord.find_or_create method"""
    with app.app_context():
        # Create new record
        record1 = WordRecord.find_or_create("test", "english", "Test definition")
        db.session.add(record1)
        db.session.commit()

        assert record1.query_times == 1

        # Find existing record
        record2 = WordRecord.find_or_create("test", "english", "Updated definition")

        assert record2.id == record1.id  # Same record
        assert record2.query_times == 2  # Incremented
        assert record2.definition == "Updated definition"  # Updated
