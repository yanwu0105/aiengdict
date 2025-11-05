# AI English-Chinese Dictionary

> 🤖 一個基於 AI 的智能英漢-漢英雙向詞典應用

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 特性

- 🎯 **智能查詢**: 基於 Google Gemini AI 的智能單詞解釋
- 🔄 **雙向翻譯**: 支持英漢、漢英雙向查詢
- 📚 **查詢歷史**: 自動保存查詢記錄，方便回顧
- 👤 **用戶系統**: 完整的用戶註冊、登入、認證功能
- 📊 **個性化歷史**: 每個用戶獨立的查詢歷史記錄
- 🎨 **現代界面**: 簡潔美觀的響應式設計
- 🔒 **安全可靠**: 密碼加密存儲，會話管理

## 🚀 快速開始

### 前置要求

- Python 3.13 或更高版本
- [uv](https://github.com/astral-sh/uv) 套件管理器（推薦）
- Google Gemini API Key

### 安裝步驟

1. **複製倉庫**

```bash
git clone https://github.com/yanwu0105/aiengdict.git
cd aiengdict
```

2. **安裝依賴**

使用 uv（推薦）:
```bash
# 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依賴
uv sync
```

或使用 pip:
```bash
pip install -r requirements.txt
```

3. **配置環境變數**

創建 `.env` 文件並添加以下配置：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Gemini API 配置
GEMINI_API_KEY=your-gemini-api-key-here

# 資料庫配置（可選，預設使用 SQLite）
DATABASE_URL=sqlite:///dictionary.db
```

**獲取 Gemini API Key**:
- 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
- 創建或登入您的 Google 帳戶
- 生成新的 API Key 並複製到 `.env` 文件

4. **初始化資料庫**

```bash
uv run python -c "from main import app; from src.database import init_database; init_database(app)"
```

5. **運行應用**

```bash
# 使用 uv
uv run python main.py

# 或使用 python
python main.py
```

應用將在 `http://localhost:3217` 啟動

## 📖 使用方法

### 基本查詢

1. 打開瀏覽器訪問 `http://localhost:3217`
2. 在搜尋框中輸入英文單詞或中文詞語
3. 點擊「查詢」按鈕或按 Enter 鍵
4. AI 將返回詳細的解釋和例句

### 用戶功能

- **註冊**: 點擊右上角「註冊」創建新帳戶
- **登入**: 使用用戶名和密碼登入
- **歷史記錄**: 登入後可查看個人查詢歷史
- **登出**: 點擊右上角用戶名，選擇「登出」

## 🏗️ 專案結構

```
aiengdict/
├── main.py                 # Flask 應用主文件
├── src/                    # 源代碼目錄
│   ├── models.py          # 資料庫模型
│   └── database.py        # 資料庫操作
├── docs/                   # 文檔目錄
│   ├── prompts.py         # AI 提示詞模板
│   └── development_plan.md # 開發計劃
├── templates/              # HTML 模板
│   ├── index.html         # 主頁
│   ├── login.html         # 登入頁
│   └── register.html      # 註冊頁
├── static/                 # 靜態資源
│   ├── css/               # 樣式文件
│   └── js/                # JavaScript 文件
├── tests/                  # 測試文件
├── scripts/                # 工具腳本
├── pyproject.toml         # 專案配置
└── README.md              # 專案說明
```

## 🛠️ 技術棧

### 後端
- **Flask 3.1.2**: Web 框架
- **SQLAlchemy 2.0.36**: ORM 資料庫操作
- **Flask-Login 0.6.3**: 用戶認證管理
- **Google Generative AI**: Gemini AI 集成

### 前端
- **Vanilla JavaScript**: 無框架依賴
- **CSS3**: 現代樣式設計
- **Fetch API**: 異步請求

### 開發工具
- **pytest**: 測試框架
- **pre-commit**: Git hooks 管理
- **commitizen**: 規範化提交
- **ruff**: 代碼格式化和檢查

## 🧪 運行測試

```bash
# 運行所有測試
uv run pytest

# 運行測試並查看覆蓋率
uv run pytest --cov=. --cov-report=html

# 運行特定測試文件
uv run pytest tests/test_main.py

# 查看詳細輸出
uv run pytest -v
```

## 📝 開發指南

### 代碼規範

專案使用 pre-commit 自動檢查代碼品質：

```bash
# 安裝 pre-commit hooks
pre-commit install

# 手動運行檢查
pre-commit run --all-files
```

### 提交規範

使用 Commitizen 規範化提交信息：

```bash
# 使用 commitizen 提交
cz commit

# 或使用傳統方式（需遵循規範）
git commit -m "feat: add new feature"
```

提交類型：
- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 構建或輔助工具

### 分支策略

- `main`: 生產分支
- `develop`: 開發分支
- `feature/*`: 功能分支
- `fix/*`: 修復分支

## 🗄️ 資料庫管理

### 查看資料庫

```bash
# 查看所有記錄
uv run python scripts/view_database.py

# 查看特定用戶的記錄
uv run python scripts/view_database.py --user-id 1
```

### 清空資料庫

```bash
# 清空所有資料（謹慎使用！）
uv run python scripts/clear_database.py
```

### 資料庫遷移

```bash
# 運行遷移腳本
uv run python scripts/migrate_database.py
```

## 🔧 環境變數說明

| 變數名 | 必需 | 預設值 | 說明 |
|--------|------|--------|------|
| `SECRET_KEY` | 是 | - | Flask 會話密鑰 |
| `GEMINI_API_KEY` | 是 | - | Google Gemini API 密鑰 |
| `FLASK_ENV` | 否 | development | 運行環境 |
| `FLASK_DEBUG` | 否 | True | 調試模式 |
| `DATABASE_URL` | 否 | sqlite:///dictionary.db | 資料庫連接 URL |

## 📊 API 端點

| 方法 | 路徑 | 說明 | 需要認證 |
|------|------|------|----------|
| GET | `/` | 主頁 | 否 |
| POST | `/lookup` | 查詢單詞 | 否 |
| GET | `/history` | 獲取歷史記錄 | 否（登入後顯示個人記錄） |
| POST | `/register` | 用戶註冊 | 否 |
| POST | `/login` | 用戶登入 | 否 |
| POST | `/logout` | 用戶登出 | 是 |
| GET | `/user/info` | 獲取用戶信息 | 否（但需登入才有資料） |

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 本倉庫
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 貢獻要求

- ✅ 遵循代碼規範
- ✅ 添加必要的測試
- ✅ 更新相關文檔
- ✅ 通過所有 CI 檢查

## 🐛 問題反饋

遇到問題？請：

1. 查看 [常見問題](#常見問題)
2. 搜尋 [Issues](https://github.com/yanwu0105/aiengdict/issues)
3. 創建新的 Issue 並提供詳細信息

## ❓ 常見問題

### Q: 如何獲取 Gemini API Key？

A: 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)，登入後即可免費獲取 API Key。

### Q: 資料庫文件存儲在哪裡？

A: 預設的 SQLite 資料庫文件 `dictionary.db` 存儲在專案根目錄。

### Q: 如何切換到 PostgreSQL？

A: 修改 `.env` 文件中的 `DATABASE_URL`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/aiengdict
```

### Q: 為什麼查詢失敗？

A: 請檢查：
1. Gemini API Key 是否正確配置
2. 網路連接是否正常
3. API 配額是否充足

### Q: 如何修改應用端口？

A: 修改 `main.py` 最後一行的 `port` 參數：
```python
app.run(debug=True, host="0.0.0.0", port=YOUR_PORT)
```

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 文件。

## 👨‍💻 作者

**AI English-Chinese Dictionary Team**

- GitHub: [@yanwu0105](https://github.com/yanwu0105)

## 🙏 致謝

- [Google Gemini](https://ai.google.dev/) - 提供強大的 AI 能力
- [Flask](https://flask.palletsprojects.com/) - 優秀的 Web 框架
- 所有貢獻者和用戶

## 🚧 開發路線圖

查看完整的開發計劃：[development_plan.md](docs/development_plan.md)

### 近期計劃
- [ ] 詞彙收藏功能
- [ ] 進階搜尋
- [ ] 學習統計
- [ ] 語音辨識

### 長期目標
- [ ] 多 AI 模型支持
- [ ] 移動端應用
- [ ] API 開放平台
- [ ] 多語言界面

---

⭐ 如果這個專案對您有幫助，請給我們一個 Star！

📧 聯絡我們：[創建 Issue](https://github.com/yanwu0105/aiengdict/issues/new)
