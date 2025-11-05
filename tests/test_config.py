"""Tests for configuration management module."""

import os
import pytest
from src.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_default_values(self, monkeypatch):
        """Test that default configuration values are set correctly."""
        # Set minimal required env vars
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
        monkeypatch.setenv("FLASK_ENV", "development")
        monkeypatch.setenv("FLASK_DEBUG", "True")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///dictionary.db")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config to pick up environment variables
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.FLASK_ENV == "development"
        assert Config.DEBUG is True
        assert Config.HOST == "0.0.0.0"
        assert Config.PORT == 3217
        assert Config.DATABASE_URL == "sqlite:///dictionary.db"
        assert Config.GEMINI_MODEL == "gemini-2.5-flash"
        assert Config.PROMPT_STYLE == "detailed"
        assert Config.RATELIMIT_ENABLED is False

    def test_config_custom_values(self, monkeypatch):
        """Test that custom configuration values override defaults."""
        monkeypatch.setenv("GEMINI_API_KEY", "custom-api-key")
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("FLASK_DEBUG", "False")
        monkeypatch.setenv("FLASK_HOST", "127.0.0.1")
        monkeypatch.setenv("FLASK_PORT", "5000")
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-pro")
        monkeypatch.setenv("PROMPT_STYLE", "standard")
        monkeypatch.setenv("RATELIMIT_ENABLED", "True")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.FLASK_ENV == "production"
        assert Config.DEBUG is False
        assert Config.HOST == "127.0.0.1"
        assert Config.PORT == 5000
        assert Config.DATABASE_URL == "postgresql://user:pass@localhost/db"
        assert Config.GEMINI_MODEL == "gemini-pro"
        assert Config.PROMPT_STYLE == "standard"
        assert Config.RATELIMIT_ENABLED is True

    def test_config_validation_missing_api_key(self, monkeypatch):
        """Test that validation fails when GEMINI_API_KEY is missing."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
            Config.validate()

    def test_config_validation_invalid_prompt_style(self, monkeypatch):
        """Test that validation fails with invalid PROMPT_STYLE."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("PROMPT_STYLE", "invalid")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        with pytest.raises(ValueError, match="PROMPT_STYLE must be"):
            Config.validate()

    def test_config_validation_invalid_port(self, monkeypatch):
        """Test that validation fails with invalid port number."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("FLASK_PORT", "70000")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        with pytest.raises(ValueError, match="FLASK_PORT must be between"):
            Config.validate()

    def test_config_validation_production_secret_key(self, monkeypatch):
        """Test that production environment requires secure SECRET_KEY."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        with pytest.raises(ValueError, match="SECRET_KEY must be set to a secure value"):
            Config.validate()

    def test_is_development(self, monkeypatch):
        """Test is_development() method."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("FLASK_ENV", "development")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.is_development() is True
        assert Config.is_production() is False
        assert Config.is_testing() is False

    def test_is_production(self, monkeypatch):
        """Test is_production() method."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("SECRET_KEY", "secure-production-key-12345")
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.is_development() is False
        assert Config.is_production() is True
        assert Config.is_testing() is False

    def test_is_testing(self, monkeypatch):
        """Test is_testing() method."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("FLASK_ENV", "testing")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.is_development() is False
        assert Config.is_production() is False
        assert Config.is_testing() is True

    def test_get_database_uri(self, monkeypatch):
        """Test get_database_uri() method."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/testdb")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.get_database_uri() == "postgresql://localhost/testdb"

    def test_config_summary(self, monkeypatch):
        """Test summary() method masks sensitive data."""
        monkeypatch.setenv("GEMINI_API_KEY", "sensitive-api-key")
        monkeypatch.setenv("FLASK_ENV", "development")
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:password@localhost/db")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        summary = Config.summary()

        assert summary["flask_env"] == "development"
        assert summary["gemini_api_key_set"] is True
        assert summary["database"] == "postgresql://***"  # Credentials masked
        assert "sensitive-api-key" not in str(summary)
        assert "password" not in str(summary)

    def test_debug_flag_parsing(self, monkeypatch):
        """Test that DEBUG flag correctly parses various boolean values."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("", False),
        ]

        for value, expected in test_cases:
            monkeypatch.setenv("GEMINI_API_KEY", "test-key")
            monkeypatch.setenv("FLASK_DEBUG", value)
            monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

            # Reload config
            import importlib
            import src.config
            importlib.reload(src.config)
            from src.config import Config

            assert Config.DEBUG is expected, f"Failed for value: {value}"

    def test_session_cookie_secure_in_production(self, monkeypatch):
        """Test that SESSION_COOKIE_SECURE is True in production."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("SECRET_KEY", "secure-key-123")
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.SESSION_COOKIE_SECURE is True
        assert Config.SESSION_COOKIE_HTTPONLY is True
        assert Config.SESSION_COOKIE_SAMESITE == "Lax"

    def test_session_cookie_not_secure_in_development(self, monkeypatch):
        """Test that SESSION_COOKIE_SECURE is False in development."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv("FLASK_ENV", "development")
        monkeypatch.setenv("SKIP_CONFIG_VALIDATION", "true")

        # Reload config
        import importlib
        import src.config
        importlib.reload(src.config)
        from src.config import Config

        assert Config.SESSION_COOKIE_SECURE is False
        assert Config.SESSION_COOKIE_HTTPONLY is True
        assert Config.SESSION_COOKIE_SAMESITE == "Lax"
