# SuRaksha – Agentic Regulatory Intelligence & Compliance
### Canara Bank · SuRaksha 2024

> An AI-powered compliance system that monitors regulatory changes, converts them to Measurable Action Points (MAPs), routes them to departments, and autonomously validates completion.

---

## 🗂️ Project Structure

```
suraksha/
├── backend/              ← FastAPI backend (shared API)
├── streamlit_app/        ← Option A: Web Dashboard
├── flutter_app/          ← Option B: Mobile App
├── data/                 ← SQLite database + sample data
├── start.bat             ← One-click launcher (Windows)
└── docker-compose.yml    ← Docker deployment
```

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Launch
```
Double-click  start.bat
```
This will:
- Create Python virtual environments
- Install all dependencies automatically
- Start the FastAPI backend on port 8000
- Start the Streamlit dashboard on port 8501
- Open the browser automatically

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Streamlit Dashboard:**
```bash
cd streamlit_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🌐 Endpoints

| Service | URL |
|---------|-----|
| **FastAPI Backend** | http://localhost:8000 |
| **API Swagger Docs** | http://localhost:8000/docs |
| **Streamlit Dashboard** | http://localhost:8501 |

---

## 📱 Flutter App (Option B)

**Prerequisites:** Flutter SDK 3.x installed

```bash
cd flutter_app
flutter pub get
flutter run                    # Android emulator / connected device
flutter run -d chrome          # Web browser
```

> **Note:** For Android emulator, the app connects to `http://10.0.2.2:8000`.
> For web/desktop, change `baseUrl` in `lib/services/api_service.dart` to `http://localhost:8000`.

---

## 🤖 Agent Architecture

| Agent | Role |
|-------|------|
| **IngestionAgent** | Scrapes RBI, SEBI, GDPR portals; parses PDFs |
| **NLPAgent** | Extracts obligations → generates MAPs using spaCy + rules |
| **RoutingAgent** | Assigns MAPs to correct departments; updates compliance scores |
| **ValidationAgent** | Runs 4-point checks: status, audit trail, evidence, deadline |

---

## 🎬 Demo Flow

1. Open dashboard → **Regulations** page
2. Paste a sample RBI/SEBI regulation text → click **Ingest**
3. Click **Generate MAPs** → watch NLP agent extract obligations
4. Switch to **MAPs** page → see cards routed to departments
5. Open a MAP → run **Validation Agent** → see checklist results
6. Switch to **Departments** → compliance scores update live
7. Go to **Alerts** → resolve an overdue alert

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| NLP | spaCy + rule-based extraction |
| Database | SQLite (aiosqlite + SQLAlchemy async) |
| Web Dashboard | Streamlit + Plotly |
| Mobile App | Flutter 3 + Dart |
| Containerization | Docker + docker-compose |

---

## 📝 Sample Regulation Texts for Demo

**RBI KYC Update:**
```
All Regulated Entities shall ensure that all existing accounts are re-KYC compliant by March 31, 2024.
Customer Due Diligence must be completed for high-risk accounts within 30 days.
IT systems must be upgraded to support Aadhaar-based eKYC by June 30, 2024.
Legal team to review all customer contracts for updated consent clauses.
Operations team shall file STRs within 24 hours of detection.
```

**SEBI AML Circular:**
```
All market intermediaries must implement enhanced transaction monitoring systems by September 2024.
Suspicious Transaction Reports must be filed within 24 hours of detection.
Risk classification of customers must be reviewed quarterly.
Operations team to maintain records for minimum 5 years.
IT department must ensure system logs are tamper-proof and immutable.
```
