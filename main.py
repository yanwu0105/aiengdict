import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import get_prompt
from src.database import init_database, save_word_record

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database
init_database(app)

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
        save_word_record(word, language, definition)

    return jsonify({"word": word, "language": language, "definition": definition})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3217)
