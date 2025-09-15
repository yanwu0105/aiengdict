"""
Test database functionality
"""

import pytest
import os
import tempfile
from flask import Flask
from src.database import save_word_record, get_query_history, create_user
from src.models import db, WordRecord, User


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


def test_save_word_record_with_user_id(app):
    """Test saving word records with user association"""
    with app.app_context():
        # Create a test user
        create_user("testuser", "test@example.com", "password123")
        user = User.find_by_username("testuser")

        # Save word record for user
        result = save_word_record("userword", "english", "User's word", user.id)
        assert result is True

        # Check if record was saved with correct user_id
        record = WordRecord.query.filter_by(
            word="userword", language="english", user_id=user.id
        ).first()
        assert record is not None
        assert record.user_id == user.id
        assert record.query_times == 1


def test_get_query_history_basic(app):
    """Test basic query history functionality"""
    with app.app_context():
        # Save some word records
        save_word_record("history1", "english", "First word")
        save_word_record("history2", "english", "Second word")
        save_word_record(
            "history1", "english", "Updated first word"
        )  # This should increment query_times

        history = get_query_history()

        assert len(history) == 2
        # Should be ordered by query_times descending
        assert history[0]["word"] == "history1"
        assert history[0]["query_times"] == 2
        assert history[1]["word"] == "history2"
        assert history[1]["query_times"] == 1


def test_get_query_history_with_user_filter(app):
    """Test query history filtered by user"""
    with app.app_context():
        # Create test users
        create_user("user1", "user1@example.com", "password123")
        create_user("user2", "user2@example.com", "password123")

        user1 = User.find_by_username("user1")
        user2 = User.find_by_username("user2")

        # Save records for different users and anonymous
        save_word_record("user1word", "english", "User 1 word", user1.id)
        save_word_record("user2word", "english", "User 2 word", user2.id)
        save_word_record("anonword", "english", "Anonymous word")  # No user_id

        # Get history for user1
        user1_history = get_query_history(user_id=user1.id)
        assert len(user1_history) == 1
        assert user1_history[0]["word"] == "user1word"

        # Get history for user2
        user2_history = get_query_history(user_id=user2.id)
        assert len(user2_history) == 1
        assert user2_history[0]["word"] == "user2word"

        # Get anonymous history
        anon_history = get_query_history(user_id=None)
        assert len(anon_history) == 1
        assert anon_history[0]["word"] == "anonword"
