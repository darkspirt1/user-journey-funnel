# User Journey Funnel Analysis Dashboard

A full-stack analytics dashboard for tracking user conversion funnels, drop-off rates, and segment-level insights — built with FastAPI, SQLite, React, and Recharts.

🔗 **Live Demo**: *(add your deployed URL here later)*

---

## What It Does

- Tracks users across 4 funnel stages: **Visit → Signup → Add to Cart → Purchase**
- Calculates **drop-off rates** at each stage transition
- Segments funnel data by **Device, Location, Traffic Source, and Age Group**
- Identifies the **biggest leakage point** automatically
- Shows **avg time spent** at each step
- Provides **fix recommendations** with impact ratings

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python, SQLite |
| Data | 5,000 synthetic users · 9,294 funnel events |
| Frontend | React (Vite), Recharts |
| Styling | Custom CSS with CSS variables |

---

## Key Insights From the Data

- **Overall conversion: 4%** — only 198 out of 5,000 visitors complete a purchase
- **Biggest drop-off: Add to Cart → Purchase (85.5%)** — checkout is the critical failure point
- **Mobile converts at 1.7%** vs Desktop at 7.3% — major mobile UX gap
- Filters update the funnel and KPIs in real time

---

## Project Structure
user-journey-funnel/
├── backend/
│   ├── database.py        # SQLite setup + seed data (5000 users)
│   ├── main.py            # FastAPI app + router registration
│   └── routers/
│       ├── funnel.py      # /api/funnel — filterable funnel stages
│       ├── segments.py    # /api/segments/* — device, location, source, age
│       └── insights.py    # /api/insights — drop-offs, recommendations
├── frontend/
│   └── src/
│       ├── App.jsx        # Main dashboard component
│       └── App.css        # Dark theme styling
└── data/
└── funnel.db          # SQLite database (git-ignored)

---

## Running Locally

**Backend**
```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn pandas
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/funnel` | Funnel stages with filter support |
| GET | `/api/segments/device` | Funnel breakdown by device |
| GET | `/api/segments/location` | Funnel breakdown by location |
| GET | `/api/segments/source` | Funnel breakdown by traffic source |
| GET | `/api/segments/age` | Funnel breakdown by age group |
| GET | `/api/insights` | Drop-offs, conversions, recommendations |



