# 💰 FinFlow - Quản lý Tiết kiệm Cá nhân

Ứng dụng web quản lý mục tiêu tiết kiệm với AI tư vấn tài chính (Python Flask + SQLite + Google Gemini).

## ✨ Tính năng chính

- 📊 Quản lý mục tiêu tiết kiệm và theo dõi tiến độ
- 💳 Quản lý tài khoản ngân hàng và giao dịch
- 🤖 AI Advisor phân tích tài chính và đề xuất kế hoạch tiết kiệm
- 👤 Đăng nhập/Đăng ký cá nhân

---

## 🚀 Cài đặt nhanh (5 phút)

### 1. Clone và cài đặt

```bash
git clone <repository-url>
cd finflow

# Tạo virtualenv (khuyến nghị)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Cài dependencies
pip install -r requirements.txt
```

### 2. Cấu hình `.env`

Tạo file `.env`:

```bash
DB_ENGINE=sqlite
DATABASE_PATH=dev.db
GEMINI_API_KEY=your_api_key_here
```

**Lấy API key miễn phí**: https://makersuite.google.com/app/apikey

### 3. Tạo database và chạy

```bash
python init_db.py    # Tạo database
python app.py        # Chạy app
```

Truy cập: **http://localhost:5000**

---

## 📂 Cấu trúc

```
finflow/
├── app.py              # Flask app + routes
├── models.py           # Database models (SQLite)
├── services.py         # Business logic
├── ai_advisor.py       # AI tư vấn (Google Gemini)
├── init_db.py          # Script tạo database
├── templates/          # HTML templates
├── static/             # CSS, JS
├── .env                # Config (DATABASE_PATH, GEMINI_API_KEY)
└── dev.db              # SQLite database (auto-generated)
```

---

## 🎯 Sử dụng cơ bản

1. **Đăng ký**: `/register` → tạo tài khoản
2. **Tạo mục tiêu**: Dashboard → "+ Thêm mục tiêu"
3. **Thêm tiền**: Nhập số tiền → "+ Thêm"
4. **AI Advisor**: Menu → "🤖 AI Advisor" → phân tích tài chính
5. **Kế hoạch AI**: Click "🤖 Kế hoạch AI" trên mỗi mục tiêu

---

## 🔧 Troubleshooting

**Lỗi `ModuleNotFoundError: No module named 'google.generativeai'`**
```bash
pip install google-generativeai==0.3.2
```

**Lỗi `404 models/gemini-pro is not found`**  
Sửa `ai_advisor.py` dòng 26:
```python
self.model = genai.GenerativeModel('gemini-1.5-flash')
```

**Lỗi `Database chưa tồn tại`**
```bash
python init_db.py
```

---

## 🚀 Deploy Production

**Gunicorn (Linux/macOS)**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Waitress (Windows)**:
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

---

## 📄 License

MIT - Free to use

---

**Tech Stack**: Flask 3.0 • SQLite • Google Gemini API  
**Version**: 1.0.0  
**Made with ❤️ for better financial management**