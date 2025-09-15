"""
Tests for database models (User and WordRecord)
"""

import pytest
import os
import tempfile
from flask import Flask
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


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self, app):
        """Test basic user creation"""
        with app.app_context():
            user = User(
                username="testuser", email="test@example.com", display_name="Test User"
            )
            user.set_password("password123")

            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.display_name == "Test User"
            assert user.is_active is True
            assert user.created_on is not None

    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")

            # Password should be hashed, not stored as plain text
            assert user.password_hash != "password123"
            assert len(user.password_hash) > 20  # Hashed passwords are longer

            # Should be able to verify correct password
            assert user.check_password("password123") is True

            # Should reject incorrect password
            assert user.check_password("wrongpassword") is False

    def test_get_display_name(self, app):
        """Test get_display_name method"""
        with app.app_context():
            # User with display name
            user1 = User(
                username="user1", email="test1@example.com", display_name="Display Name"
            )
            assert user1.get_display_name() == "Display Name"

            # User without display name should fallback to username
            user2 = User(username="user2", email="test2@example.com")
            assert user2.get_display_name() == "user2"

    def test_find_by_username(self, app):
        """Test finding user by username"""
        with app.app_context():
            user = User(username="findme", email="findme@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Should find existing user
            found_user = User.find_by_username("findme")
            assert found_user is not None
            assert found_user.username == "findme"

            # Should return None for non-existent user
            not_found = User.find_by_username("notexist")
            assert not_found is None

    def test_find_by_email(self, app):
        """Test finding user by email"""
        with app.app_context():
            user = User(username="emailuser", email="email@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Should find existing user
            found_user = User.find_by_email("email@example.com")
            assert found_user is not None
            assert found_user.email == "email@example.com"

            # Should return None for non-existent email
            not_found = User.find_by_email("notexist@example.com")
            assert not_found is None

    def test_user_repr(self, app):
        """Test user string representation"""
        with app.app_context():
            user = User(username="repruser", email="repr@example.com")
            assert str(user) == "<User repruser>"


class TestWordRecordModel:
    """Test WordRecord model functionality"""

    def test_word_record_creation(self, app):
        """Test basic word record creation"""
        with app.app_context():
            record = WordRecord(
                word="test",
                language="english",
                definition="A test definition",
                query_times=1,
            )
            db.session.add(record)
            db.session.commit()

            assert record.id is not None
            assert record.word == "test"
            assert record.language == "english"
            assert record.definition == "A test definition"
            assert record.query_times == 1
            assert record.user_id is None  # Anonymous record
            assert record.created_on is not None
            assert record.updated_on is not None

    def test_word_record_with_user(self, app):
        """Test word record creation with user association"""
        with app.app_context():
            # Create user first
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Create word record for user
            record = WordRecord(
                word="userword",
                language="english",
                definition="User's word definition",
                query_times=1,
                user_id=user.id,
            )
            db.session.add(record)
            db.session.commit()

            assert record.user_id == user.id
            assert record.user == user

    def test_find_or_create_new_record(self, app):
        """Test find_or_create with new record"""
        with app.app_context():
            record = WordRecord.find_or_create("newword", "english", "New definition")

            assert record.word == "newword"
            assert record.language == "english"
            assert record.definition == "New definition"
            assert record.query_times == 1
            assert record.user_id is None

    def test_find_or_create_existing_record(self, app):
        """Test find_or_create with existing record"""
        with app.app_context():
            # Create initial record
            record1 = WordRecord.find_or_create(
                "existing", "english", "Original definition"
            )
            db.session.add(record1)
            db.session.commit()
            original_id = record1.id

            # Find existing record
            record2 = WordRecord.find_or_create(
                "existing", "english", "Updated definition"
            )

            assert record2.id == original_id  # Same record
            assert record2.query_times == 2  # Incremented
            assert record2.definition == "Updated definition"  # Updated

    def test_find_or_create_with_user(self, app):
        """Test find_or_create with user association"""
        with app.app_context():
            # Create user
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Create record for user
            record1 = WordRecord.find_or_create(
                "userword", "english", "Definition", user.id
            )
            db.session.add(record1)
            db.session.commit()

            # Same word for same user should update existing
            record2 = WordRecord.find_or_create(
                "userword", "english", "Updated definition", user.id
            )
            assert record2.id == record1.id
            assert record2.query_times == 2

            # Same word for different user (or anonymous) should create new
            record3 = WordRecord.find_or_create(
                "userword", "english", "Anonymous definition", None
            )
            assert record3.id != record1.id
            assert record3.query_times == 1

    def test_word_record_repr(self, app):
        """Test word record string representation"""
        with app.app_context():
            record = WordRecord(
                word="repr", language="english", definition="test", query_times=1
            )
            assert str(record) == "<WordRecord repr (english)>"

    def test_unique_constraint(self, app):
        """Test unique constraint behavior through find_or_create method"""
        with app.app_context():
            # Create first record using find_or_create
            record1 = WordRecord.find_or_create(
                "unique", "english", "def1", user_id=None
            )
            db.session.add(record1)
            db.session.commit()

            # Try to create same record again - should return existing record
            record2 = WordRecord.find_or_create(
                "unique", "english", "def2", user_id=None
            )

            # Should be the same record (find_or_create prevents duplicates)
            assert record2.id == record1.id
            assert record2.query_times == 2  # Should be incremented
            assert record2.definition == "def2"  # Should be updated


class TestUserWordRecordRelationship:
    """Test relationship between User and WordRecord models"""

    def test_user_word_records_relationship(self, app):
        """Test user can access their word records"""
        with app.app_context():
            # Create user
            user = User(username="reluser", email="rel@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Create multiple word records for user
            record1 = WordRecord(
                word="word1", language="english", definition="def1", user_id=user.id
            )
            record2 = WordRecord(
                word="word2", language="chinese", definition="def2", user_id=user.id
            )
            db.session.add_all([record1, record2])
            db.session.commit()

            # User should have access to their records
            user_records = user.word_records.all()
            assert len(user_records) == 2
            assert record1 in user_records
            assert record2 in user_records

    def test_word_record_user_relationship(self, app):
        """Test word record can access its user"""
        with app.app_context():
            # Create user
            user = User(username="owner", email="owner@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Create word record for user
            record = WordRecord(
                word="owned",
                language="english",
                definition="owned word",
                user_id=user.id,
            )
            db.session.add(record)
            db.session.commit()

            # Record should have access to its user
            assert record.user == user
            assert record.user.username == "owner"
