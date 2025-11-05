"""
Configuration management module for aiengdict application.

This module provides a centralized configuration system that:
- Loads environment variables from .env file
- Provides type-safe configuration access
- Validates required configuration values
- Supports different environments (development, production, testing)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class with environment variable support."""

    # Flask configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # Server configuration
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FLASK_PORT", "3217"))

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///dictionary.db")

    # AI configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Prompt configuration
    PROMPT_STYLE: str = os.getenv("PROMPT_STYLE", "detailed")

    # Security configuration
    MAX_CONTENT_LENGTH: int = int(
        os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))
    )  # 16MB
    SESSION_COOKIE_SECURE: bool = FLASK_ENV == "production"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Rate limiting configuration (to be implemented)
    RATELIMIT_ENABLED: bool = os.getenv("RATELIMIT_ENABLED", "False").lower() in (
        "true",
        "1",
        "yes",
    )
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "200 per day, 50 per hour")

    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration values.

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        errors = []

        # Check required fields
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY must be set in environment variables")

        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-change-in-production":
            if cls.FLASK_ENV == "production":
                errors.append(
                    "SECRET_KEY must be set to a secure value in production environment"
                )

        # Validate PROMPT_STYLE
        if cls.PROMPT_STYLE not in ("standard", "detailed"):
            errors.append(
                f"PROMPT_STYLE must be 'standard' or 'detailed', got '{cls.PROMPT_STYLE}'"
            )

        # Validate PORT
        if not (1 <= cls.PORT <= 65535):
            errors.append(f"FLASK_PORT must be between 1 and 65535, got {cls.PORT}")

        if errors:
            raise ValueError(
                "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.FLASK_ENV == "development"

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.FLASK_ENV == "production"

    @classmethod
    def is_testing(cls) -> bool:
        """Check if running in testing environment."""
        return cls.FLASK_ENV == "testing"

    @classmethod
    def get_database_uri(cls) -> str:
        """Get the database URI for SQLAlchemy."""
        return cls.DATABASE_URL

    @classmethod
    def summary(cls) -> dict:
        """
        Get a summary of current configuration (without sensitive data).

        Returns:
            dict: Configuration summary with sensitive values masked
        """
        return {
            "flask_env": cls.FLASK_ENV,
            "debug": cls.DEBUG,
            "host": cls.HOST,
            "port": cls.PORT,
            "database": cls.DATABASE_URL.split("://")[0] + "://***",  # Hide credentials
            "gemini_model": cls.GEMINI_MODEL,
            "prompt_style": cls.PROMPT_STYLE,
            "gemini_api_key_set": bool(cls.GEMINI_API_KEY),
            "ratelimit_enabled": cls.RATELIMIT_ENABLED,
        }


# Validate configuration on module import (can be disabled for testing)
if os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    try:
        Config.validate()
    except ValueError as e:
        # In development, just warn; in production, fail fast
        if Config.is_production():
            raise
        print(f"⚠️  Configuration warning: {e}")
