"""
Database models for AI English Dictionary
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


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
    created_on: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Create unique constraint on word + language combination
    __table_args__ = (
        db.UniqueConstraint("word", "language", name="unique_word_language"),
    )

    def __repr__(self):
        return f"<WordRecord {self.word} ({self.language})>"

    @classmethod
    def find_or_create(cls, word: str, language: str, definition: str):
        """
        Find existing record or create new one
        Updates query_times and definition if exists
        """
        existing = cls.query.filter_by(word=word, language=language).first()

        if existing:
            # Update existing record
            existing.definition = definition
            existing.query_times += 1
            existing.updated_on = datetime.utcnow()
            return existing
        else:
            # Create new record
            return cls(
                word=word, language=language, definition=definition, query_times=1
            )
