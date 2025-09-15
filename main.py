import os
import re
from flask import Flask, render_template, request, jsonify
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import google.generativeai as genai
from dotenv import load_dotenv
from docs.prompts import get_prompt
from src.database import (
    init_database,
    save_word_record,
    get_query_history,
    create_user,
    authenticate_user,
)
from src.models import User

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# Initialize database
init_database(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "請先登入以使用此功能"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Prompt style configuration (can be changed for testing)
PROMPT_STYLE = "detailed"  # Options: "standard" or "detailed"


def detect_language(text):
    """Detect if input text is Chinese or English"""
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
    return "chinese" if chinese_pattern.search(text) else "english"


def get_word_definition(word, language):
    """Get word definition using Gemini API"""
    try:
        # Get prompt from prompts.py
        prompt_template = get_prompt(language, PROMPT_STYLE)
        prompt = prompt_template.format(word=word)

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"查詢時發生錯誤: {str(e)}"


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/lookup", methods=["POST"])
def lookup_word():
    """API endpoint for word lookup"""
    data = request.get_json()
    word = data.get("word", "").strip()

    if not word:
        return jsonify({"error": "請輸入要查詢的單詞"}), 400

    language = detect_language(word)
    definition = get_word_definition(word, language)

    # Save to database if query was successful (no error message)
    if not definition.startswith("查詢時發生錯誤"):
        user_id = current_user.id if current_user.is_authenticated else None
        save_word_record(word, language, definition, user_id)

    return jsonify({"word": word, "language": language, "definition": definition})


@app.route("/history", methods=["GET"])
def get_history():
    """API endpoint for getting query history"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        history = get_query_history(user_id=user_id)
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": f"獲取歷史記錄失敗: {str(e)}"}), 500


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    display_name = data.get("display_name", "").strip() or None

    if not username or not email or not password:
        return jsonify({"error": "請填寫所有必填欄位"}), 400

    if len(password) < 6:
        return jsonify({"error": "密碼長度至少6個字符"}), 400

    success, message = create_user(username, email, password, display_name)

    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "請輸入用戶名和密碼"}), 400

    user, message = authenticate_user(username, password)

    if user:
        login_user(user, remember=True)
        return jsonify(
            {
                "message": message,
                "user": {
                    "username": user.username,
                    "display_name": user.get_display_name(),
                },
            }
        )
    else:
        return jsonify({"error": message}), 401


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """User logout"""
    logout_user()
    return jsonify({"message": "登出成功"})


@app.route("/user/info", methods=["GET"])
def user_info():
    """Get current user info"""
    if current_user.is_authenticated:
        return jsonify(
            {
                "authenticated": True,
                "user": {
                    "username": current_user.username,
                    "display_name": current_user.get_display_name(),
                    "email": current_user.email,
                },
            }
        )
    else:
        return jsonify({"authenticated": False})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3217)
