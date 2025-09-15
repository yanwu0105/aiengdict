"""
Tests for authentication-related database functions
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from flask import Flask
from src.database import (
    create_user,
    authenticate_user,
    save_word_record,
    get_query_history,
)
from src.models import db, User, WordRecord


@pytest.fixture
def app():
    """Create test Flask app with temporary database"""
    app = Flask(__name__)

    # Use temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


class TestCreateUser:
    """Test create_user function"""

    def test_create_user_success(self, app):
        """Test successful user creation"""
        with app.app_context():
            success, message = create_user(
                "testuser", "test@example.com", "password123", "Test User"
            )

            assert success is True
            assert message == "註冊成功"

            # Verify user was created in database
            user = User.find_by_username("testuser")
            assert user is not None
            assert user.email == "test@example.com"
            assert user.display_name == "Test User"
            assert user.check_password("password123") is True

    def test_create_user_without_display_name(self, app):
        """Test user creation without display name"""
        with app.app_context():
            success, message = create_user(
                "testuser2", "test2@example.com", "password123"
            )

            assert success is True
            assert message == "註冊成功"

            user = User.find_by_username("testuser2")
            assert user is not None
            assert user.display_name is None

    def test_create_user_duplicate_username(self, app):
        """Test creating user with duplicate username"""
        with app.app_context():
            # Create first user
            create_user("duplicate", "user1@example.com", "password123")

            # Try to create second user with same username
            success, message = create_user(
                "duplicate", "user2@example.com", "password456"
            )

            assert success is False
            assert message == "用戶名已存在"

    def test_create_user_duplicate_email(self, app):
        """Test creating user with duplicate email"""
        with app.app_context():
            # Create first user
            create_user("user1", "duplicate@example.com", "password123")

            # Try to create second user with same email
            success, message = create_user(
                "user2", "duplicate@example.com", "password456"
            )

            assert success is False
            assert message == "電子郵件已被註冊"

    def test_create_user_database_error(self, app):
        """Test handling database errors during user creation"""
        with app.app_context():
            # Mock database error by patching the database session
            with patch("src.database.db.session.commit") as mock_commit:
                mock_commit.side_effect = Exception("Database connection error")

                success, message = create_user(
                    "erroruser", "error@example.com", "password123"
                )

                assert success is False
                assert "註冊失敗，請稍後再試" in message


class TestAuthenticateUser:
    """Test authenticate_user function"""

    def setup_test_user(self, app):
        """Helper to create a test user"""
        with app.app_context():
            success, _ = create_user(
                "authuser", "auth@example.com", "password123", "Auth User"
            )
            assert success is True
            return User.find_by_username("authuser")

    def test_authenticate_user_with_username(self, app):
        """Test authentication with username"""
        self.setup_test_user(app)

        with app.app_context():
            user, message = authenticate_user("authuser", "password123")

            assert user is not None
            assert message == "登入成功"
            assert user.username == "authuser"

    def test_authenticate_user_with_email(self, app):
        """Test authentication with email"""
        self.setup_test_user(app)

        with app.app_context():
            user, message = authenticate_user("auth@example.com", "password123")

            assert user is not None
            assert message == "登入成功"
            assert user.email == "auth@example.com"

    def test_authenticate_user_wrong_password(self, app):
        """Test authentication with wrong password"""
        self.setup_test_user(app)

        with app.app_context():
            user, message = authenticate_user("authuser", "wrongpassword")

            assert user is None
            assert message == "密碼錯誤"

    def test_authenticate_user_nonexistent_user(self, app):
        """Test authentication with non-existent user"""
        with app.app_context():
            user, message = authenticate_user("nonexistent", "password123")

            assert user is None
            assert message == "用戶不存在"

    def test_authenticate_user_inactive_user(self, app):
        """Test authentication with inactive user"""
        with app.app_context():
            # Create user and make inactive
            success, _ = create_user("inactive", "inactive@example.com", "password123")
            assert success is True

            user = User.find_by_username("inactive")
            user.is_active = False
            db.session.commit()

            # Try to authenticate
            auth_user, message = authenticate_user("inactive", "password123")

            assert auth_user is None
            assert message == "帳戶已被停用"

    def test_authenticate_user_updates_last_login(self, app):
        """Test that successful authentication updates last_login"""
        self.setup_test_user(app)

        with app.app_context():
            user_before = User.find_by_username("authuser")
            original_last_login = user_before.last_login

            user_after, message = authenticate_user("authuser", "password123")

            assert user_after is not None
            assert message == "登入成功"
            assert user_after.last_login != original_last_login
            assert user_after.last_login is not None


class TestSaveWordRecordWithUser:
    """Test save_word_record function with user support"""

    def setup_test_user(self, app):
        """Helper to create a test user"""
        with app.app_context():
            success, _ = create_user("worduser", "word@example.com", "password123")
            assert success is True
            return User.find_by_username("worduser")

    def test_save_word_record_with_user(self, app):
        """Test saving word record with user association"""
        user = self.setup_test_user(app)

        with app.app_context():
            result = save_word_record("hello", "english", "Greeting", user.id)
            assert result is True

            record = WordRecord.query.filter_by(
                word="hello", language="english", user_id=user.id
            ).first()
            assert record is not None
            assert record.user_id == user.id
            assert record.query_times == 1

    def test_save_word_record_anonymous(self, app):
        """Test saving word record without user (anonymous)"""
        with app.app_context():
            result = save_word_record("anonymous", "english", "Anonymous word")
            assert result is True

            record = WordRecord.query.filter_by(
                word="anonymous", language="english", user_id=None
            ).first()
            assert record is not None
            assert record.user_id is None
            assert record.query_times == 1

    def test_save_word_record_user_vs_anonymous(self, app):
        """Test that same word can be saved for user and anonymous separately"""
        user = self.setup_test_user(app)

        with app.app_context():
            # Save for user
            save_word_record("shared", "english", "User definition", user.id)

            # Save for anonymous
            save_word_record("shared", "english", "Anonymous definition")

            # Should have two separate records
            user_record = WordRecord.query.filter_by(
                word="shared", user_id=user.id
            ).first()
            anon_record = WordRecord.query.filter_by(
                word="shared", user_id=None
            ).first()

            assert user_record is not None
            assert anon_record is not None
            assert user_record.id != anon_record.id
            assert user_record.definition == "User definition"
            assert anon_record.definition == "Anonymous definition"


class TestGetQueryHistoryWithUser:
    """Test get_query_history function with user support"""

    def setup_test_data(self, app):
        """Helper to create test users and word records"""
        with app.app_context():
            # Create users
            create_user("user1", "user1@example.com", "password123")
            create_user("user2", "user2@example.com", "password123")

            user1 = User.find_by_username("user1")
            user2 = User.find_by_username("user2")

            # Create word records for user1
            save_word_record("hello", "english", "Hello def", user1.id)
            save_word_record("world", "english", "World def", user1.id)

            # Create word records for user2
            save_word_record("test", "english", "Test def", user2.id)

            # Create anonymous records
            save_word_record("anonymous1", "english", "Anon def 1")
            save_word_record("anonymous2", "english", "Anon def 2")

            return user1, user2

    def test_get_query_history_for_user(self, app):
        """Test getting query history for specific user"""
        user1, user2 = self.setup_test_data(app)

        with app.app_context():
            # Refresh user objects to avoid DetachedInstanceError
            user1 = User.find_by_username("user1")
            history = get_query_history(user_id=user1.id)

            # Should only get user1's records
            assert len(history) == 2
            words = [record["word"] for record in history]
            assert "hello" in words
            assert "world" in words
            assert "test" not in words  # user2's record
            assert "anonymous1" not in words  # anonymous record

    def test_get_query_history_anonymous(self, app):
        """Test getting query history for anonymous users"""
        self.setup_test_data(app)

        with app.app_context():
            history = get_query_history(user_id=None)

            # Should only get anonymous records
            assert len(history) == 2
            words = [record["word"] for record in history]
            assert "anonymous1" in words
            assert "anonymous2" in words
            assert "hello" not in words  # user record
            assert "test" not in words  # user record

    def test_get_query_history_with_limit(self, app):
        """Test query history with limit parameter"""
        user1, _ = self.setup_test_data(app)

        with app.app_context():
            # Refresh user objects to avoid DetachedInstanceError
            user1 = User.find_by_username("user1")
            # Add more records for user1
            for i in range(5):
                save_word_record(f"word{i}", "english", f"Definition {i}", user1.id)

            # Test limit
            history = get_query_history(limit=3, user_id=user1.id)
            assert len(history) <= 3

    def test_get_query_history_ordered_by_query_times(self, app):
        """Test that history is ordered by query_times descending"""
        user1, _ = self.setup_test_data(app)

        with app.app_context():
            # Refresh user objects to avoid DetachedInstanceError
            user1 = User.find_by_username("user1")
            # Query "hello" multiple times to increase query_times
            save_word_record("hello", "english", "Hello def updated", user1.id)
            save_word_record("hello", "english", "Hello def updated again", user1.id)

            history = get_query_history(user_id=user1.id)

            # "hello" should be first (highest query_times)
            assert len(history) >= 2
            assert history[0]["word"] == "hello"
            assert history[0]["query_times"] == 3  # 1 + 2 updates
