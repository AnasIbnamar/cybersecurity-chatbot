# CyberGuard — AI Cybersecurity Assistant

A professional AI-powered cybersecurity platform built with Python, Flask, and large language model APIs. CyberGuard provides real-time security guidance, automated threat analysis, and expert-level cybersecurity advice — accessible to users at every skill level, no account required.

---

## Features

### Security Tools (no AI key required)
| Tool | Chat Shortcut | Description |
|---|---|---|
| Password Analyzer | `password: YourPass` | Strength scoring, entropy analysis, weakness detection, improvement tips |
| Password Generator | Sidebar → Password Analyzer | Cryptographically secure passwords via Python `secrets` module |
| Phishing Detector | `phish: email text` | 15+ indicator analysis with risk scoring and severity badges |
| Scam Detector | `scam: message` | Pattern matching for 20+ fraud and social engineering tactics |
| URL Safety Checker | `url: https://...` | Heuristic analysis for phishing URLs, suspicious TLDs, brand impersonation |

### AI Assistant
- Groq (`llama-3.3-70b-versatile`, free tier) or OpenAI (`gpt-4o-mini`) as provider
- Expert cybersecurity system prompt covering passwords, phishing, malware, VPNs, 2FA, privacy, cloud security, and incident response
- Persistent conversation history within session, isolated per user
- Graceful fallback messaging when API quota is exhausted

### Security Guides (built-in static content)
- **Device Security Checklist** — 30 actionable hardening steps across 6 categories
- **Wi-Fi Security Guide** — Router hardening, password hygiene, public Wi-Fi safety, IoT isolation, VPN guidance

### Admin Analytics Dashboard (`/admin`)
- Total scans, message counts, tool breakdown with percentage bars
- Daily scan activity over the last 7 days
- Recent activity log (last 20 tool invocations)

### Landing Page (`/`)
- Professional product landing page with hero, features grid, how-it-works, security principles, FAQ, and CTA
- Sticky header with smooth-scroll navigation

### Professional UI
- Pure dark SaaS aesthetic — near-black background with violet (#8b5cf6) accent
- SVG sprite icon system — no external font libraries, no emoji
- Sidebar navigation with topic shortcuts, tool access, and session controls
- Markdown-rendered AI responses with copy-to-clipboard
- Responsive mobile layout with hamburger menu
- About & Privacy modal with disclaimer, privacy notice, and technical details

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x |
| **AI** | Groq API (`llama-3.3-70b-versatile`) / OpenAI API (`gpt-4o-mini`) |
| **Database** | SQLite via `sqlite3` (messages, tool_usage, exports) |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (no framework) |
| **Security** | Input sanitisation, in-memory rate limiting, HTTPOnly cookies |
| **Deployment** | Gunicorn, Render / Railway / Fly.io ready |

---

## Architecture

```
cyberguard/
├── app.py                       # Application factory (create_app)
├── config.py                    # Environment-based configuration
├── requirements.txt
├── Procfile                     # Gunicorn entry point
├── .env.example
│
├── routes/
│   ├── chat.py                  # /chat and /reset — AI + tool shortcut endpoints
│   ├── tools.py                 # /api/* — REST endpoints for all security tools
│   └── admin.py                 # /admin — analytics dashboard
│
├── services/
│   └── ai_service.py            # Groq/OpenAI client, system prompt, error hierarchy
│
├── simulators/
│   ├── password_checker.py      # Strength analysis + cryptographically secure generator
│   ├── phishing_detector.py     # 15-indicator phishing analysis engine
│   ├── scam_detector.py         # 20+ scam pattern recogniser
│   └── url_checker.py           # 11-check heuristic URL safety analyser
│
├── utils/
│   ├── sanitizer.py             # Input length capping + HTML escaping
│   ├── rate_limiter.py          # In-memory IP-based rate limiting decorator
│   └── logger.py                # Structured application logging
│
├── database/
│   └── db.py                    # SQLite helpers: init, save_message, log_tool_usage, get_admin_stats
│
├── static/
│   ├── style.css                # Full CSS design system (dark theme, SVG icons, responsive)
│   └── favicon.svg              # Inline SVG shield+lock icon
│
├── templates/
│   ├── landing.html             # Public landing page (/)
│   ├── index.html               # Main SPA dashboard (/dashboard)
│   └── admin.html               # Analytics dashboard (/admin)
│
└── docs/
    └── PORTFOLIO.md             # CV bullet points, LinkedIn post, recruiter pitch
```

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- A free Groq API key from [console.groq.com](https://console.groq.com) (recommended) **or** an OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cyberguard.git
cd cyberguard
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
GROQ_API_KEY=your_groq_key_here     # free at console.groq.com
SECRET_KEY=change_this_to_a_long_random_string
```

### 5. Run the development server
```bash
python app.py
```

Open your browser at:
- `http://localhost:5000` — Landing page
- `http://localhost:5000/dashboard` — Main security dashboard
- `http://localhost:5000/admin` — Analytics dashboard

## Live Demo

https://cybersecurity-chatbot-cd27.onrender.com
---

## API Reference

All tool endpoints accept `Content-Type: application/json` and return JSON.

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/chat` | `{ "message": "..." }` | AI chat or tool shortcut trigger |
| `POST` | `/reset` | — | Clear session conversation history |
| `POST` | `/api/password-check` | `{ "password": "..." }` | Analyse password strength |
| `POST` | `/api/generate-password` | `{ "length": 16 }` | Generate secure password |
| `POST` | `/api/phishing-check` | `{ "text": "..." }` | Analyse email for phishing |
| `POST` | `/api/scam-check` | `{ "text": "..." }` | Analyse message for scam patterns |
| `POST` | `/api/url-check` | `{ "url": "..." }` | Check URL for safety indicators |
| `GET` | `/api/stats` | — | Tool usage counts (JSON) |

### Chat shortcut triggers
Sending a message to `/chat` with these prefixes bypasses the AI and routes directly to the security tool:

```
password: MyPassword123    → Password strength analysis
phish: email body...       → Phishing detection
scam: suspicious message   → Scam pattern detection
url: https://example.com   → URL safety check
```

---

## Security Features

- **Input sanitisation** on all user-submitted text (length capping + HTML escaping)
- **Session isolation** — each browser session has its own conversation history
- **In-memory rate limiting** on all API endpoints (no Redis required)
- **HTTPOnly + SameSite** session cookie flags set in production config
- **Debug mode** automatically disabled when `FLASK_ENV=production`
- **No persistent storage** of analysed content beyond the current session
- **Heuristic-only analysis** — pasted content never reaches third-party scan APIs
- **Graceful AI fallback** — security tools remain fully functional when AI API is unavailable

---

## Deployment

### Render

1. Push to a GitHub repository
2. Create a new **Web Service** on Render
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `gunicorn app:app --workers 2 --timeout 120`
5. Add environment variables:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (free at console.groq.com) |
| `SECRET_KEY` | A long random string |
| `FLASK_ENV` | `production` |

### Railway / Fly.io

The included `Procfile` handles startup automatically:
```
web: gunicorn app:app --workers 2 --timeout 120
```

> **Note:** SQLite databases do not persist between deploys on ephemeral file systems. For persistent analytics, swap SQLite for PostgreSQL via `flask-sqlalchemy`.

---

## Roadmap

| Feature | Status |
|---|---|
| Password Analyzer | Done |
| Phishing Detector | Done |
| Scam Detector | Done |
| URL Safety Checker | Done |
| Device Security Checklist | Done |
| Wi-Fi Security Guide | Done |
| Admin Analytics Dashboard | Done |
| Landing Page | Done |
| Breach Exposure Checker (HIBP API) | Planned |
| Account Recovery Assistant | Planned |
| Dark/Light theme toggle | Planned |
| PostgreSQL support | Planned |
| Exportable PDF security report | Planned |

---

## Disclaimer

CyberGuard is an AI-powered guidance tool designed for **defensive security awareness and education**. It does not provide hacking instructions, assist with unauthorised access, or replace professional incident response services. For active security incidents, contact a qualified cybersecurity professional or your organisation's security team.

Security scanner results are based on heuristic pattern matching and should be treated as indicators, not definitive verdicts. Always exercise independent judgment when making security decisions.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
