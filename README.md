# 🏠 AI-Powered House Plan Generator

Generate intelligent **top-view 2D floor plans** from natural language using Gemini AI or OpenAI. Get 3 unique layout variations, refine them with conversational feedback, and export professional PDFs — all running on a low-end laptop.

---

## ✨ Features

- **Natural language input** — "Modern 2BHK north-facing house with parking"
- **3 layout variations** — Grid, Vastu-compliant, and Open Plan
- **AI-powered parsing** — Gemini 1.5 Flash or GPT-3.5 (or rule-based fallback — no API key needed)
- **Feedback refinement** — "Make kitchen bigger" → regenerates instantly
- **PDF export** — Professional multi-page PDF with dimensions
- **Cost estimation** — Rough construction cost in INR
- **Vastu scoring** — Compass-based room placement score
- **Works offline** — Rule-based fallback needs no internet

---

## 🖥️ System Requirements

| Component | Minimum |
|-----------|---------|
| OS | Windows 10/11, Ubuntu 20+, macOS 12+ |
| RAM | 4 GB (8 GB recommended) |
| CPU | Intel i3 or equivalent |
| Python | 3.9 or higher |
| Node.js | 18 or higher |
| Disk | 500 MB free |

---

## 🚀 Quick Start (Windows)

```bat
# 1. Clone or download the project
# 2. Double-click:
run_project.bat
```

The script will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Prompt you to add your Gemini API key
4. Start both backend and frontend
5. Open http://localhost:3000 in your browser

---

## 📦 Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux

# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
# AI_PROVIDER=gemini

# Start backend
python app.py
```

Backend runs at: **http://localhost:5000**

### Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

Frontend runs at: **http://localhost:3000**

---

## 🔑 Getting an API Key

### Gemini (Recommended — Free)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Add to `backend/.env`: `GEMINI_API_KEY=your_key`

### OpenAI (Alternative)
1. Go to https://platform.openai.com/api-keys
2. Create a key
3. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=your_key
   AI_PROVIDER=openai
   ```

### No API Key (Rule-Based Fallback)
Leave both keys empty — the app still works using built-in rules. Form inputs are used directly without AI natural language understanding.

---

## 🎯 How to Use

1. **Enter plot dimensions** (width × depth in feet, e.g., 30×40)
2. **Choose facing direction** (North, South, East, West, etc.)
3. **Set bedrooms and bathrooms** count
4. **Check additional spaces** (parking, balcony, dining, etc.)
5. **Type natural language instructions** (optional but powerful)
6. Click **Generate Floor Plans**
7. View 3 plan variations in the gallery
8. **Give feedback** to refine: "Increase kitchen size" / "Add balcony"
9. Click **Download PDF** for a professional export

---

## 💬 Natural Language Examples

```
"Modern 2BHK east-facing house with vastu compliance and parking"
"I want a north-facing house with pooja room and study"
"3BHK contemporary design with open kitchen and large balcony"
"Keep kitchen in southeast corner as per vastu"
"Increase master bedroom size and move bathroom adjacent to it"
"Compact 1BHK for a single professional, minimalist design"
```

---

## 📁 Project Structure

```
genai-topview-house-planner/
├── backend/
│   ├── app.py              ← Flask REST API (4 endpoints)
│   ├── ai_parser.py        ← Gemini/OpenAI + rule-based fallback
│   ├── generator.py        ← Layout engine + SVG rendering
│   ├── constraints.py      ← Room rules, Vastu, min sizes
│   ├── feedback_engine.py  ← Feedback processing pipeline
│   ├── pdf_generator.py    ← ReportLab PDF export
│   ├── database.py         ← SQLite storage
│   ├── utils.py            ← Shared utilities
│   ├── requirements.txt
│   ├── .env.example
│   └── generated/          ← Auto-created: SVGs + PDFs
│
├── frontend/
│   ├── src/
│   │   ├── App.js                      ← Main app + state
│   │   ├── api.js                      ← Axios API calls
│   │   ├── index.js                    ← React entry
│   │   ├── components/
│   │   │   ├── InputForm.jsx           ← Form UI
│   │   │   ├── PlanCard.jsx            ← Plan display
│   │   │   ├── FeedbackPanel.jsx       ← Feedback UI
│   │   │   └── LoadingOverlay.jsx      ← Loading screen
│   │   └── styles/
│   │       └── App.css                 ← Blueprint aesthetic
│   ├── public/index.html
│   └── package.json
│
├── docs/
│   └── project_report.md   ← Architecture + API docs
│
├── README.md
└── run_project.bat         ← Windows one-click launcher
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Backend status check |
| POST | `/api/generate` | Generate 3 floor plans |
| POST | `/api/feedback` | Refine plans with feedback |
| GET | `/api/session/{id}` | Get session history |
| POST | `/api/download-pdf` | Generate & stream PDF |
| GET | `/generated/{file}` | Serve SVG/PDF files |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|---------|
| Backend won't start | Check Python 3.9+ installed; activate venv first |
| `CORS error` in browser | Ensure Flask is running on port 5000 |
| Plans not generating | Check `.env` has valid API key, or leave blank for rule-based |
| SVG not showing | Check `/generated/` folder exists in backend directory |
| PDF download fails | Install reportlab: `pip install reportlab` |
| `Module not found` | Run `pip install -r requirements.txt` again |
| Frontend blank page | Run `npm install` then `npm start` |

---

## 🌐 Google Colab Backend

See `docs/project_report.md` Section 7 for full Colab setup instructions using ngrok tunneling.

---

## 📄 License

MIT License — Free for personal and commercial use.

---

*Built with React + Flask + Gemini AI · Generates plans in seconds on low-end hardware*
