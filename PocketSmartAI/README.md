# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application for budget-aware recommendations across:

- Home interior planning
- Party/event planning
- Jewelry planning with optional outfit-image analysis

The project follows the uploaded PocketSmart AI documentation: modular routes/services/models, authentication, session data, recommendation history, dynamic frontend rendering, platform shopping links, Gemini multimodal support, and deterministic fallback recommendations.

## Important model note

The source document specifies **Gemini 1.5 Flash Pro**. That model is no longer the safest default for a new 2026 build, so this implementation makes the Gemini model configurable through `GEMINI_MODEL` and defaults to a current Gemini Flash model. Set the variable to any model available to your account if needed.

## Quick start

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY`. A Gemini API key is optional for local demo mode; without it the app uses deterministic fallback recommendations.

```powershell
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

### macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

## Gemini setup

Create a Gemini API key, then set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
AI_ENABLED=true
```

The application sends text prompts for Home and Party planners. Jewelry sends the prompt plus the uploaded outfit image when an image is provided.

## Testing

Run:

```bash
pytest -q
```

The tests cover health, registration/login, protected routes, fallback recommendation generation, and planner validation.

## Project structure

```text
PocketSmartAI/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── models/
│   │   ├── db.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── pages.py
│   │   └── planners.py
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── platform_links.py
│   │   └── recommendation_service.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── home_planner.html
│   │   ├── party_planner.html
│   │   ├── jewelry_planner.html
│   │   └── history.html
│   └── static/
│       ├── styles.css
│       ├── app.js
│       └── uploads/
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
