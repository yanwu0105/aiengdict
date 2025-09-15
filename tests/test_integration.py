"""
Integration tests for the complete authentication and dictionary system
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import LoginManager
from src.models import User
from src.database import init_database


@pytest.fixture
def app():
    """Create test Flask app with complete setup"""
    app = Flask(__name__)

    # Use temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    # Initialize database
    init_database(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register all routes
    from main import index, lookup_word, get_history, register, login, logout, user_info

    app.add_url_rule("/", "index", index, methods=["GET"])
    app.add_url_rule("/lookup", "lookup_word", lookup_word, methods=["POST"])
    app.add_url_rule("/history", "get_history", get_history, methods=["GET"])
    app.add_url_rule("/register", "register", register, methods=["GET", "POST"])
    app.add_url_rule("/login", "login", login, methods=["GET", "POST"])
    app.add_url_rule("/logout", "logout", logout, methods=["POST"])
    app.add_url_rule("/user/info", "user_info", user_info, methods=["GET"])

    with app.app_context():
        yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def mock_gemini():
    """Mock Gemini API responses"""
    with patch("main.model.generate_content") as mock:
        mock_response = MagicMock()
        mock_response.text = "Mocked AI definition with detailed explanation"
        mock.return_value = mock_response
        yield mock


class TestCompleteUserFlow:
    """Test complete user registration, login, and usage flow"""

    def test_anonymous_user_flow(self, client, mock_gemini):
        """Test complete flow for anonymous users"""
        # 1. Check initial user status (should be anonymous)
        response = client.get("/user/info")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["authenticated"] is False

        # 2. Look up a word (should save to anonymous history)
        response = client.post(
            "/lookup",
            data=json.dumps({"word": "anonymous"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["word"] == "anonymous"
        assert data["language"] == "english"

        # 3. Check history (should show anonymous record)
        response = client.get("/history")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "anonymous"

    def test_registered_user_complete_flow(self, client, mock_gemini):
        """Test complete flow for registered users"""
        user_data = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "password123",
            "display_name": "Integration User",
        }

        # 1. Register new user
        response = client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        assert response.status_code == 200

        # 2. Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )
        assert response.status_code == 200

        # 3. Check user status (should be authenticated)
        response = client.get("/user/info")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["authenticated"] is True
        assert data["user"]["username"] == user_data["username"]

        # 4. Look up words (should save to user's history)
        words_to_lookup = ["integration", "testing", "authentication"]
        for word in words_to_lookup:
            response = client.post(
                "/lookup",
                data=json.dumps({"word": word}),
                content_type="application/json",
            )
            assert response.status_code == 200

        # 5. Check history (should show user's records only)
        response = client.get("/history")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["history"]) == 3
        history_words = [record["word"] for record in data["history"]]
        for word in words_to_lookup:
            assert word in history_words

        # 6. Look up same word again (should increment query_times)
        response = client.post(
            "/lookup",
            data=json.dumps({"word": "integration"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 7. Check that query_times increased
        response = client.get("/history")
        data = json.loads(response.data)
        integration_record = next(
            r for r in data["history"] if r["word"] == "integration"
        )
        assert integration_record["query_times"] == 2

        # 8. Logout
        response = client.post("/logout")
        assert response.status_code == 200

        # 9. Check user status (should be anonymous again)
        response = client.get("/user/info")
        data = json.loads(response.data)
        assert data["authenticated"] is False

    def test_multiple_users_isolation(self, client, mock_gemini):
        """Test that multiple users have isolated histories"""
        # Create and login first user
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user1_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user1_data["username"], "password": user1_data["password"]}
            ),
            content_type="application/json",
        )

        # User1 looks up words
        client.post(
            "/lookup",
            data=json.dumps({"word": "user1word"}),
            content_type="application/json",
        )

        # Check user1's history
        response = client.get("/history")
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "user1word"

        # Logout user1
        client.post("/logout")

        # Create and login second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user2_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user2_data["username"], "password": user2_data["password"]}
            ),
            content_type="application/json",
        )

        # User2 looks up different words
        client.post(
            "/lookup",
            data=json.dumps({"word": "user2word"}),
            content_type="application/json",
        )

        # Check user2's history (should not see user1's words)
        response = client.get("/history")
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "user2word"

    def test_anonymous_vs_user_isolation(self, client, mock_gemini):
        """Test that anonymous and user histories are separate"""
        # Anonymous user looks up word
        response = client.post(
            "/lookup",
            data=json.dumps({"word": "anonymousword"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Check anonymous history
        response = client.get("/history")
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "anonymousword"

        # Register and login user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user_data["username"], "password": user_data["password"]}
            ),
            content_type="application/json",
        )

        # User looks up word
        client.post(
            "/lookup",
            data=json.dumps({"word": "userword"}),
            content_type="application/json",
        )

        # Check user history (should not see anonymous word)
        response = client.get("/history")
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "userword"

        # Logout and check anonymous history again
        client.post("/logout")
        response = client.get("/history")
        data = json.loads(response.data)
        assert len(data["history"]) == 1
        assert data["history"][0]["word"] == "anonymousword"


class TestErrorHandlingIntegration:
    """Test error handling across the integrated system"""

    def test_database_error_handling(self, client):
        """Test graceful handling of database errors"""
        # Try to register with invalid data that might cause database error
        invalid_data = {
            "username": "",  # Empty username might cause validation error
            "email": "invalid-email",
            "password": "123",
        }

        response = client.post(
            "/register", data=json.dumps(invalid_data), content_type="application/json"
        )

        # Should return error, not crash
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_api_error_propagation(self, client):
        """Test that API errors are properly handled and don't affect user state"""
        # Register and login user
        user_data = {
            "username": "errortest",
            "email": "error@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user_data["username"], "password": user_data["password"]}
            ),
            content_type="application/json",
        )

        # Mock API error
        with patch("main.model.generate_content") as mock_api:
            mock_api.side_effect = Exception("API Error")

            response = client.post(
                "/lookup",
                data=json.dumps({"word": "errorword"}),
                content_type="application/json",
            )

            # Should return error response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "查詢時發生錯誤" in data["definition"]

        # User should still be logged in
        response = client.get("/user/info")
        data = json.loads(response.data)
        assert data["authenticated"] is True

    def test_session_persistence_across_requests(self, client):
        """Test that user sessions persist properly across multiple requests"""
        # Register and login
        user_data = {
            "username": "sessiontest",
            "email": "session@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        login_response = client.post(
            "/login",
            data=json.dumps(
                {"username": user_data["username"], "password": user_data["password"]}
            ),
            content_type="application/json",
        )
        assert login_response.status_code == 200

        # Make multiple requests to different endpoints
        endpoints_to_test = ["/user/info", "/history", "/user/info", "/history"]

        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            assert response.status_code == 200

            if endpoint == "/user/info":
                data = json.loads(response.data)
                assert data["authenticated"] is True
                assert data["user"]["username"] == user_data["username"]


class TestPerformanceAndScalability:
    """Test system behavior under various load conditions"""

    def test_multiple_word_lookups_performance(self, client, mock_gemini):
        """Test system performance with multiple word lookups"""
        # Register and login user
        user_data = {
            "username": "perftest",
            "email": "perf@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user_data["username"], "password": user_data["password"]}
            ),
            content_type="application/json",
        )

        # Look up many words
        words = [f"word{i}" for i in range(50)]

        for word in words:
            response = client.post(
                "/lookup",
                data=json.dumps({"word": word}),
                content_type="application/json",
            )
            assert response.status_code == 200

        # Check that history is properly limited and ordered
        response = client.get("/history")
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should be limited to 20 records (default limit)
        assert len(data["history"]) == 20

        # Should be ordered by query_times (all should be 1 in this case, so order by creation)
        for record in data["history"]:
            assert record["query_times"] == 1

    def test_history_with_repeated_queries(self, client, mock_gemini):
        """Test history ordering with repeated queries"""
        # Register and login user
        user_data = {
            "username": "repeattest",
            "email": "repeat@example.com",
            "password": "password123",
        }
        client.post(
            "/register", data=json.dumps(user_data), content_type="application/json"
        )
        client.post(
            "/login",
            data=json.dumps(
                {"username": user_data["username"], "password": user_data["password"]}
            ),
            content_type="application/json",
        )

        # Look up words with different frequencies
        words_and_counts = [("frequent", 5), ("medium", 3), ("rare", 1), ("common", 4)]

        for word, count in words_and_counts:
            for _ in range(count):
                client.post(
                    "/lookup",
                    data=json.dumps({"word": word}),
                    content_type="application/json",
                )

        # Check history ordering
        response = client.get("/history")
        data = json.loads(response.data)

        # Should be ordered by query_times descending
        expected_order = ["frequent", "common", "medium", "rare"]
        actual_order = [record["word"] for record in data["history"]]

        assert actual_order == expected_order
        assert data["history"][0]["query_times"] == 5  # frequent
        assert data["history"][1]["query_times"] == 4  # common
        assert data["history"][2]["query_times"] == 3  # medium
        assert data["history"][3]["query_times"] == 1  # rare
