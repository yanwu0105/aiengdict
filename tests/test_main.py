"""
Tests for main.py Flask application
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, detect_language, get_word_definition


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response"""
    mock_response = MagicMock()
    mock_response.text = "Mocked AI response with translation and definition"
    return mock_response


class TestDetectLanguage:
    """Test language detection function"""

    def test_detect_chinese_characters(self):
        """Test detection of Chinese characters"""
        assert detect_language("你好") == "chinese"
        assert detect_language("學習") == "chinese"
        assert detect_language("中文字典") == "chinese"

    def test_detect_english_characters(self):
        """Test detection of English characters"""
        assert detect_language("hello") == "english"
        assert detect_language("learning") == "english"
        assert detect_language("dictionary") == "english"

    def test_detect_mixed_content_with_chinese(self):
        """Test detection of mixed content containing Chinese"""
        assert detect_language("hello 你好") == "chinese"
        assert detect_language("學習 English") == "chinese"

    def test_detect_numbers_and_symbols(self):
        """Test detection of numbers and symbols (should default to English)"""
        assert detect_language("123") == "english"
        assert detect_language("!@#$") == "english"
        assert detect_language("") == "english"

    def test_detect_whitespace_only(self):
        """Test detection of whitespace-only input"""
        assert detect_language("   ") == "english"
        assert detect_language("\n\t") == "english"


class TestGetWordDefinition:
    """Test word definition function"""

    @patch("main.model.generate_content")
    def test_get_chinese_word_definition(self, mock_generate, mock_gemini_response):
        """Test getting definition for Chinese word"""
        mock_generate.return_value = mock_gemini_response

        result = get_word_definition("學習", "chinese")

        assert result == "Mocked AI response with translation and definition"
        mock_generate.assert_called_once()

    @patch("main.model.generate_content")
    def test_get_english_word_definition(self, mock_generate, mock_gemini_response):
        """Test getting definition for English word"""
        mock_generate.return_value = mock_gemini_response

        result = get_word_definition("learning", "english")

        assert result == "Mocked AI response with translation and definition"
        mock_generate.assert_called_once()

    @patch("main.model.generate_content")
    def test_get_word_definition_api_error(self, mock_generate):
        """Test handling of API errors"""
        mock_generate.side_effect = Exception("API Error")

        result = get_word_definition("test", "english")

        assert "查詢時發生錯誤" in result
        assert "API Error" in result

    @patch("main.model.generate_content")
    def test_prompt_contains_word(self, mock_generate, mock_gemini_response):
        """Test that the generated prompt contains the word"""
        mock_generate.return_value = mock_gemini_response

        get_word_definition("測試", "chinese")

        # Check that generate_content was called with a prompt containing the word
        call_args = mock_generate.call_args[0][0]
        assert "測試" in call_args


class TestFlaskRoutes:
    """Test Flask application routes"""

    def test_index_route(self, client):
        """Test the main index route"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"html" in response.data.lower()

    def test_lookup_route_valid_request(self, client):
        """Test lookup route with valid request"""
        with patch("main.get_word_definition") as mock_get_def:
            mock_get_def.return_value = "Test definition"

            response = client.post(
                "/lookup",
                data=json.dumps({"word": "test"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["word"] == "test"
            assert data["language"] == "english"
            assert data["definition"] == "Test definition"

    def test_lookup_route_chinese_word(self, client):
        """Test lookup route with Chinese word"""
        with patch("main.get_word_definition") as mock_get_def:
            mock_get_def.return_value = "中文定義"

            response = client.post(
                "/lookup",
                data=json.dumps({"word": "測試"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["word"] == "測試"
            assert data["language"] == "chinese"
            assert data["definition"] == "中文定義"

    def test_lookup_route_empty_word(self, client):
        """Test lookup route with empty word"""
        response = client.post(
            "/lookup", data=json.dumps({"word": ""}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "請輸入要查詢的單詞" in data["error"]

    def test_lookup_route_whitespace_word(self, client):
        """Test lookup route with whitespace-only word"""
        response = client.post(
            "/lookup", data=json.dumps({"word": "   "}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_lookup_route_missing_word_field(self, client):
        """Test lookup route with missing word field"""
        response = client.post(
            "/lookup", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_lookup_route_invalid_json(self, client):
        """Test lookup route with invalid JSON"""
        response = client.post(
            "/lookup", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400

    def test_lookup_route_get_method_not_allowed(self, client):
        """Test that GET method is not allowed for lookup route"""
        response = client.get("/lookup")
        assert response.status_code == 405


class TestAppConfiguration:
    """Test Flask app configuration"""

    def test_app_exists(self):
        """Test that Flask app is created"""
        assert app is not None
        assert app.name == "main"

    def test_app_has_required_routes(self):
        """Test that app has required routes"""
        with app.test_client() as client:
            # Test that routes exist (even if they return errors)
            response = client.get("/")
            assert response.status_code != 404

            response = client.post(
                "/lookup", data="{}", content_type="application/json"
            )
            # Should not be 404 (route exists), might be 400 (bad request)
            assert response.status_code != 404


class TestIntegration:
    """Integration tests"""

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    @patch("main.model.generate_content")
    def test_full_lookup_flow(self, mock_generate, client):
        """Test complete lookup flow from request to response"""
        mock_response = MagicMock()
        mock_response.text = "Complete definition with examples"
        mock_generate.return_value = mock_response

        response = client.post(
            "/lookup",
            data=json.dumps({"word": "integration"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify complete response structure
        assert "word" in data
        assert "language" in data
        assert "definition" in data
        assert data["word"] == "integration"
        assert data["language"] == "english"
        assert data["definition"] == "Complete definition with examples"


class TestHistoryRoute:
    """Test query history endpoint"""

    def test_history_route_anonymous(self, client):
        """Test history route for anonymous users"""
        with patch("main.get_query_history") as mock_get_history:
            mock_get_history.return_value = [
                {
                    "word": "test",
                    "language": "english",
                    "query_times": 1,
                    "definition": "Test def",
                    "updated_on": "2024-01-01 12:00",
                }
            ]

            response = client.get("/history")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "history" in data
            assert len(data["history"]) == 1
            # Should be called with user_id=None for anonymous users
            mock_get_history.assert_called_with(user_id=None)

    def test_history_route_error(self, client):
        """Test history route with database error"""
        with patch("main.get_query_history") as mock_get_history:
            mock_get_history.side_effect = Exception("Database error")

            response = client.get("/history")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "獲取歷史記錄失敗" in data["error"]


class TestUserAwareWordLookup:
    """Test word lookup with user awareness"""

    def test_lookup_saves_with_user_context(self, client):
        """Test that word lookup considers user context when saving"""
        with patch("main.get_word_definition") as mock_get_def, patch(
            "main.save_word_record"
        ) as mock_save, patch("main.current_user") as mock_user:
            # Mock successful definition
            mock_get_def.return_value = "Test definition"

            # Mock anonymous user
            mock_user.is_authenticated = False

            response = client.post(
                "/lookup",
                data=json.dumps({"word": "test"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            # Should save with user_id=None for anonymous users
            mock_save.assert_called_once_with(
                "test", "english", "Test definition", None
            )

    def test_lookup_error_not_saved(self, client):
        """Test that failed lookups are not saved to database"""
        with patch("main.get_word_definition") as mock_get_def, patch(
            "main.save_word_record"
        ) as mock_save:
            # Mock error response
            mock_get_def.return_value = "查詢時發生錯誤: API Error"

            response = client.post(
                "/lookup",
                data=json.dumps({"word": "test"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            # Should not save error responses
            mock_save.assert_not_called()
