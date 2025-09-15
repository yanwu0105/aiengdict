"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
from unittest.mock import patch

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables for all tests"""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test_api_key_12345",
            "FLASK_ENV": "testing",
            "FLASK_DEBUG": "False",
            "TESTING": "1",
            "DATABASE_URL": "sqlite:///:memory:",
        },
    ):
        yield


@pytest.fixture
def sample_words():
    """Sample words for testing"""
    return {
        "chinese": ["你好", "學習", "字典", "測試", "電腦"],
        "english": ["hello", "learning", "dictionary", "test", "computer"],
        "mixed": ["hello 你好", "test 測試"],
        "special": ["123", "!@#", "", "   ", "\n\t"],
    }


@pytest.fixture
def mock_api_responses():
    """Mock API responses for different scenarios"""
    return {
        "success": "Detailed word definition with examples and translations",
        "chinese_response": "【單詞】: 測試\n【英文翻譯】: test\n【詞性】: [noun]\n【英文解釋】: A procedure to check something",
        "english_response": "【Word】: test\n【詞性】: [noun]\n【中文翻譯】: 測試\n【英文解釋】: A procedure to check something",
        "error": "API rate limit exceeded",
    }


@pytest.fixture
def app_config():
    """Flask app configuration for testing"""
    return {"TESTING": True, "WTF_CSRF_ENABLED": False, "SECRET_KEY": "test-secret-key"}


@pytest.fixture
def test_users():
    """Sample test users data"""
    return {
        "user1": {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "password123",
            "display_name": "Test User 1",
        },
        "user2": {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "password456",
            "display_name": "Test User 2",
        },
        "admin": {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "display_name": "Administrator",
        },
    }


@pytest.fixture
def sample_word_records():
    """Sample word records for testing"""
    return [
        {
            "word": "hello",
            "language": "english",
            "definition": "A greeting word",
            "query_times": 3,
        },
        {
            "word": "world",
            "language": "english",
            "definition": "The earth and all people",
            "query_times": 1,
        },
        {
            "word": "你好",
            "language": "chinese",
            "definition": "中文問候語",
            "query_times": 2,
        },
    ]
