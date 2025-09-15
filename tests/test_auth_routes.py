"""
Tests for authentication routes and endpoints
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch
from flask import Flask
from flask_login import LoginManager
from src.models import User
from src.database import init_database, create_user


@pytest.fixture
def app():
    """Create test Flask app with authentication setup"""
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

    # Import and register routes
    from main import register, login, logout, user_info

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
def test_user_data():
    """Test user data for registration/login"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "display_name": "Test User",
    }


class TestRegisterRoute:
    """Test user registration endpoint"""

    def test_register_get_request(self, client):
        """Test GET request to register page"""
        with patch("main.render_template") as mock_render:
            mock_render.return_value = "<html><body>Register Page</body></html>"
            response = client.get("/register")
            assert response.status_code == 200
            mock_render.assert_called_once_with("register.html")

    def test_register_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "註冊成功" in data["message"]

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com",
            # Missing password
        }

        response = client.post(
            "/register",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "請填寫所有必填欄位" in data["error"]

    def test_register_short_password(self, client, test_user_data):
        """Test registration with password too short"""
        test_user_data["password"] = "12345"  # Less than 6 characters

        response = client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "密碼長度至少6個字符" in data["error"]

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username"""
        # Register first user
        client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )

        # Try to register second user with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"

        response = client.post(
            "/register",
            data=json.dumps(duplicate_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "用戶名已存在" in data["error"]

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )

        # Try to register second user with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"

        response = client.post(
            "/register",
            data=json.dumps(duplicate_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "電子郵件已被註冊" in data["error"]

    def test_register_without_display_name(self, client, test_user_data):
        """Test registration without display name (optional field)"""
        del test_user_data["display_name"]

        response = client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data


class TestLoginRoute:
    """Test user login endpoint"""

    def setup_test_user(self, app, test_user_data):
        """Helper to create a test user"""
        with app.app_context():
            success, _ = create_user(
                test_user_data["username"],
                test_user_data["email"],
                test_user_data["password"],
                test_user_data.get("display_name"),
            )
            assert success is True

    def test_login_get_request(self, client):
        """Test GET request to login page"""
        with patch("main.render_template") as mock_render:
            mock_render.return_value = "<html><body>Login Page</body></html>"
            response = client.get("/login")
            assert response.status_code == 200
            mock_render.assert_called_once_with("login.html")

    def test_login_success_with_username(self, client, app, test_user_data):
        """Test successful login with username"""
        self.setup_test_user(app, test_user_data)

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "登入成功" in data["message"]
        assert "user" in data
        assert data["user"]["username"] == test_user_data["username"]

    def test_login_success_with_email(self, client, app, test_user_data):
        """Test successful login with email"""
        self.setup_test_user(app, test_user_data)

        login_data = {
            "username": test_user_data["email"],  # Using email as username
            "password": test_user_data["password"],
        }

        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "登入成功" in data["message"]

    def test_login_wrong_password(self, client, app, test_user_data):
        """Test login with wrong password"""
        self.setup_test_user(app, test_user_data)

        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword",
        }

        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "密碼錯誤" in data["error"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {"username": "nonexistent", "password": "password123"}

        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "用戶不存在" in data["error"]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        incomplete_data = {"username": "testuser"}  # Missing password

        response = client.post(
            "/login", data=json.dumps(incomplete_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "請輸入用戶名和密碼" in data["error"]


class TestLogoutRoute:
    """Test user logout endpoint"""

    def login_test_user(self, client, app, test_user_data):
        """Helper to create and login a test user"""
        with app.app_context():
            create_user(
                test_user_data["username"],
                test_user_data["email"],
                test_user_data["password"],
                test_user_data.get("display_name"),
            )

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )
        assert response.status_code == 200

    def test_logout_success(self, client, app, test_user_data):
        """Test successful logout"""
        self.login_test_user(client, app, test_user_data)

        response = client.post("/logout")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "登出成功" in data["message"]

    def test_logout_without_login(self, client):
        """Test logout without being logged in"""
        # Flask-Login should redirect or return error for @login_required
        response = client.post("/logout")
        # Depending on Flask-Login configuration, this might be redirect or error
        assert response.status_code in [401, 302]  # 401 Unauthorized or 302 Redirect


class TestUserInfoRoute:
    """Test user info endpoint"""

    def test_user_info_authenticated(self, client, app, test_user_data):
        """Test user info when authenticated"""
        # Create and login user
        with app.app_context():
            create_user(
                test_user_data["username"],
                test_user_data["email"],
                test_user_data["password"],
                test_user_data.get("display_name"),
            )

        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        # Get user info
        response = client.get("/user/info")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["authenticated"] is True
        assert "user" in data
        assert data["user"]["username"] == test_user_data["username"]
        assert data["user"]["email"] == test_user_data["email"]

    def test_user_info_not_authenticated(self, client):
        """Test user info when not authenticated"""
        response = client.get("/user/info")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["authenticated"] is False
        assert "user" not in data


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_register_login_logout_flow(self, client, app, test_user_data):
        """Test complete registration -> login -> logout flow"""
        # 1. Register
        register_response = client.post(
            "/register",
            data=json.dumps(test_user_data),
            content_type="application/json",
        )
        assert register_response.status_code == 200

        # 2. Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        login_response = client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )
        assert login_response.status_code == 200

        # 3. Check user info (should be authenticated)
        info_response = client.get("/user/info")
        assert info_response.status_code == 200
        info_data = json.loads(info_response.data)
        assert info_data["authenticated"] is True

        # 4. Logout
        logout_response = client.post("/logout")
        assert logout_response.status_code == 200

        # 5. Check user info again (should not be authenticated)
        info_response2 = client.get("/user/info")
        assert info_response2.status_code == 200
        info_data2 = json.loads(info_response2.data)
        assert info_data2["authenticated"] is False

    def test_session_persistence(self, client, app, test_user_data):
        """Test that user session persists across requests"""
        # Create and login user
        with app.app_context():
            create_user(
                test_user_data["username"],
                test_user_data["email"],
                test_user_data["password"],
            )

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        client.post(
            "/login", data=json.dumps(login_data), content_type="application/json"
        )

        # Make multiple requests - session should persist
        for _ in range(3):
            response = client.get("/user/info")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["authenticated"] is True
