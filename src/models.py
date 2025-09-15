"""
Database models for AI English Dictionary
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Model for user authentication and profile"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationship with word records
    word_records: Mapped[list["WordRecord"]] = relationship(
        "WordRecord", back_populates="user", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_display_name(self) -> str:
        """Get display name or fallback to username"""
        return self.display_name or self.username

    @classmethod
    def find_by_username(cls, username: str):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()


class WordRecord(db.Model):
    """Model for storing word lookup records"""

    __tablename__ = "word_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'chinese' or 'english'
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    query_times: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )  # Allow null for anonymous users
    created_on: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship with user
    user: Mapped["User"] = relationship("User", back_populates="word_records")

    # Create unique constraint on word + language + user combination
    __table_args__ = (
        db.UniqueConstraint(
            "word", "language", "user_id", name="unique_word_language_user"
        ),
    )

    def __repr__(self):
        return f"<WordRecord {self.word} ({self.language})>"

    @classmethod
    def find_or_create(
        cls, word: str, language: str, definition: str, user_id: int = None
    ):
        """
        Find existing record or create new one
        Updates query_times and definition if exists
        """
        existing = cls.query.filter_by(
            word=word, language=language, user_id=user_id
        ).first()

        if existing:
            # Update existing record
            existing.definition = definition
            existing.query_times += 1
            existing.updated_on = datetime.now(timezone.utc)
            return existing
        else:
            # Create new record
            return cls(
                word=word,
                language=language,
                definition=definition,
                query_times=1,
                user_id=user_id,
            )
