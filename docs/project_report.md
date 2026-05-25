# AI-Powered House Plan Generator — Project Report

## 1. Project Overview

An AI-powered web application that generates intelligent **top-view 2D floor plans** from natural language input and structured form data. Users can iteratively refine plans through conversational feedback.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  InputForm → API calls → PlanCard Gallery → FeedbackPanel│
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP REST (axios)
┌─────────────────────▼───────────────────────────────────┐
│                    BACKEND (Flask)                        │
│                                                           │
│  app.py (REST API)                                        │
│    ↓                                                      │
│  ai_parser.py ──→ Gemini/OpenAI API (or rule fallback)   │
│    ↓                                                      │
│  generator.py ──→ SVG floor plans (3 variations)         │
│    ↓                                                      │
│  pdf_generator.py ──→ reportlab PDF export               │
│    ↓                                                      │
│  database.py ──→ SQLite (sessions + plans + feedback)    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Key Components

### Backend Modules

| File | Purpose |
|------|---------|
| `app.py` | Flask REST API — 4 endpoints |
| `ai_parser.py` | Gemini/OpenAI integration + rule-based fallback |
| `generator.py` | CSP + rule-based layout engine, SVG rendering |
| `constraints.py` | Room sizes, Vastu rules, adjacency rules |
| `feedback_engine.py` | Feedback parsing and plan regeneration |
| `pdf_generator.py` | ReportLab PDF export |
| `database.py` | SQLite session/plan storage |
| `utils.py` | Shared utilities |

### Frontend Components

| File | Purpose |
|------|---------|
| `App.js` | Main app state, layout orchestration |
| `InputForm.jsx` | Plot/room inputs + natural language box |
| `PlanCard.jsx` | Individual floor plan display |
| `FeedbackPanel.jsx` | Conversational feedback UI |
| `LoadingOverlay.jsx` | Full-screen loading indicator |
| `api.js` | All axios HTTP calls |

---

## 4. Generation Engine

Three distinct layout strategies produce Plan A, B, and C:

- **Plan A — Grid Layout**: Systematic left-to-right, top-to-bottom room placement. Efficient space usage.
- **Plan B — Vastu Layout**: Rooms placed per Vastu Shastra compass zones (NE for hall, SE for kitchen, SW for master bedroom, etc.)
- **Plan C — Open Plan**: Modern separation of public zones (hall, kitchen, dining) vs. private zones (bedrooms).

Each plan is rendered as an SVG with:
- Colour-coded rooms
- Room labels + dimensions in feet
- Plot boundary with compass
- Entrance marker per facing direction

---

## 5. API Endpoints

### POST `/api/generate`
Generate 3 floor plan variations from user inputs.

**Request:**
```json
{
  "plot_width": 30,
  "plot_height": 40,
  "facing": "north",
  "bedrooms": 2,
  "bathrooms": 2,
  "parking": true,
  "natural_text": "modern house with vastu compliance"
}
```

**Response:**
```json
{
  "session_id": "abc123...",
  "bhk": "2BHK",
  "plans": [
    {
      "plan_name": "Plan A",
      "style": "Grid Layout",
      "rooms": [...],
      "image_url": "/generated/abc123_Plan_A_iter1.svg"
    }
  ],
  "vastu_score": { "score": 80, "rating": "Good" },
  "cost_estimate": { "estimated_cost_lakhs": 45.5 }
}
```

### POST `/api/feedback`
Update constraints and regenerate based on natural language feedback.

**Request:**
```json
{
  "session_id": "abc123...",
  "feedback": "Increase kitchen size and add balcony",
  "iteration": 2
}
```

### GET `/api/session/{session_id}`
Retrieve stored session including feedback history.

### POST `/api/download-pdf`
Generate and stream PDF as a file download.

### GET `/generated/{filename}`
Serve generated SVG/PNG/PDF files.

---

## 6. AI Integration

The AI layer (Gemini 1.5 Flash / GPT-3.5) does two things:

1. **Requirement parsing**: Converts natural language + form inputs into a structured JSON constraint object
2. **Feedback parsing**: Converts feedback text into constraint delta (what to add/remove/resize)

If no API key is configured, a **rule-based fallback parser** handles all inputs without any AI dependency.

---

## 7. Running on Google Colab

To run the backend on Colab and frontend locally:

```python
# In a Colab cell:
!pip install flask flask-cors python-dotenv google-generativeai reportlab matplotlib svgwrite

# Set your API key
import os
os.environ["GEMINI_API_KEY"] = "your_key_here"

# Install ngrok for public URL
!pip install pyngrok
from pyngrok import ngrok

# Start Flask in background
import threading
def run_flask():
    os.chdir("/content/backend")
    os.system("python app.py")

threading.Thread(target=run_flask, daemon=True).start()

# Create public tunnel
public_url = ngrok.connect(5000)
print(f"Backend URL: {public_url}")
```

Then in `frontend/src/api.js`, change:
```js
const BASE_URL = "https://your-ngrok-url.ngrok.io";
```

---

## 8. Future Enhancements

- [ ] Drag-and-drop room repositioning (React DnD)
- [ ] Multi-floor plans (basement, first floor)
- [ ] Furniture placement suggestions
- [ ] 3D preview using Three.js (optional)
- [ ] Share plans via URL
- [ ] Export as DXF/AutoCAD format
- [ ] Material quantity estimation
- [ ] Neighbourhood context (sun path, wind direction)
- [ ] Mobile app (React Native)

---

## 9. Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 | Component-based, fast dev |
| Backend | Flask 3 | Lightweight Python server |
| AI | Gemini 1.5 Flash | Fast, free tier, great JSON output |
| Layout | Custom CSP engine | No GPU, CPU-only, lightweight |
| Visualization | SVGWrite | Pure Python SVG, no display needed |
| PDF | ReportLab | Production-grade, no browser needed |
| Database | SQLite | Zero setup, file-based |
| Styling | Custom CSS | No Tailwind bloat, full control |

---

*Generated by AI House Plan Generator v1.0*
