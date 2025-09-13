import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def detect_language(text):
    """Detect if input text is Chinese or English"""
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
    return "chinese" if chinese_pattern.search(text) else "english"


def get_word_definition(word, language):
    """Get word definition using Gemini API"""
    try:
        if language == "chinese":
            prompt = f"""
            請提供中文詞彙「{word}」的詳細解釋，包括：
            1. 英文翻譯
            2. 詞性
            3. 詳細定義
            4. 使用例句（中英對照）

            請以清晰易懂的格式回答。
            """
        else:
            prompt = f"""
            Please provide a detailed explanation for the English word "{word}", including:
            1. Chinese translation
            2. Part of speech
            3. Detailed definition
            4. Example sentences (with Chinese translation)

            Please format the response clearly.
            """

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

    return jsonify({"word": word, "language": language, "definition": definition})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3217)
