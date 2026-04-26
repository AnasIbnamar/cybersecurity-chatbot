# CyberGuard — Portfolio & Career Materials

---

## CV Bullet Points

Use these in a Projects section under your CV/resume. Pick 3–4 that match the role you're applying for.

**General-purpose (any tech role):**
- Built **CyberGuard**, a full-stack AI cybersecurity platform using Python/Flask, integrating Groq and OpenAI LLM APIs with a modular Blueprint architecture, serving 5 independent security analysis tools from a single application factory
- Designed and implemented 4 heuristic security engines (password strength, phishing detection, scam recognition, URL safety) using zero external scan APIs — all analysis runs server-side within the request lifecycle
- Built a professional SaaS-style dark-theme UI with a vanilla JS SPA, SVG sprite icon system, custom Markdown renderer, and responsive mobile layout — no front-end framework dependency

**Security-focused role:**
- Implemented multi-indicator phishing detection (15+ checks), scam pattern recognition (20+ tactics), and URL safety analysis (11 heuristics) covering brand impersonation, suspicious TLDs, URL obfuscation, and credential harvesting patterns
- Designed a security-first Flask application with input sanitisation on all endpoints, in-memory rate limiting, session isolation, HTTPOnly/SameSite cookie flags, and heuristic-only analysis to prevent user data from reaching third-party APIs

**Backend/API role:**
- Built a REST API layer with 7 endpoints across 3 Flask Blueprints, including AI chat routing, security tool analysis, and an admin analytics dashboard — all behind a rate-limiting decorator
- Implemented an AI provider abstraction layer supporting Groq (`llama-3.3-70b-versatile`) and OpenAI (`gpt-4o-mini`) with a custom exception hierarchy (`AIQuotaError`, `AIAuthError`, `AIConnectionError`) and graceful degradation to tool-only mode

**Data/analytics role:**
- Built an SQLite-backed analytics system tracking tool usage, daily scan volume, and conversation history; exposed via a server-rendered admin dashboard (`/admin`) using Jinja2 with usage percentage bars and activity logs

---

## LinkedIn Post

Use this when you publish the project on GitHub:

---

**Just shipped CyberGuard — an AI cybersecurity assistant I built from scratch**

Over the past few weeks I built CyberGuard: a full-stack cybersecurity platform that combines LLM-powered guidance with real security analysis tools.

**What it does:**
- Analyses passwords for strength and entropy issues
- Detects phishing red flags in suspicious emails (15+ indicators)
- Identifies scam patterns in messages (gift cards, advance fee fraud, impersonation, and 20+ more)
- Checks URLs for phishing indicators: suspicious TLDs, brand impersonation, URL shorteners, IP domains
- AI assistant for questions on malware, VPNs, 2FA, incident response, and more

**What I learned building it:**
- How to structure a Flask app properly using Blueprints, an application factory, and layered services
- How heuristic security analysis actually works under the hood — the same patterns used by real scanners
- How to design a UI that feels professional without a component library (all vanilla JS + CSS custom properties)
- How to handle LLM API failures gracefully so the product still works when the AI is down

**Tech:** Python, Flask, SQLite, Groq API, vanilla JS/CSS, Gunicorn, Render

GitHub: [link]

---

## Recruiter Pitch (60 seconds)

*For phone screens or networking conversations:*

"I recently built a full-stack cybersecurity platform called CyberGuard. It's a Flask application that combines an LLM-powered AI assistant with four heuristic security tools I built myself — a password strength analyser, phishing detector, scam recogniser, and URL safety checker. None of them use external scan APIs; all the analysis runs locally.

The interesting engineering challenge was building pattern-matching engines that produce risk scores and specific indicators, then surfacing that in a clean UI without any front-end framework. I also built a provider abstraction for Groq and OpenAI so the app degrades gracefully when the AI is unavailable.

The project is deployed and open source — it covers security, backend API design, AI integration, and product design all in one codebase."

---

## Screenshot Strategy

These are the screens that make the strongest impression for a portfolio:

1. **Landing page hero** — shows product thinking and design quality, not just code
2. **Chat view with a multi-step AI response** — use a realistic question like "What should I do if I received a phishing email?" — demonstrates AI integration and Markdown rendering
3. **Phishing Detector result** — paste a sample phishing email and take a screenshot with the risk indicators expanded (use a public example from phishing.org/examples)
4. **URL Checker result** — check a known phishing URL pattern (e.g. `http://paypal-secure-update.tk/login/verify`) — shows the HIGH RISK verdict and badge system
5. **Password Analyzer result** — use a weak password like `password123` — shows the strength meter and feedback items
6. **Admin Dashboard** — shows you thought about analytics and product metrics, not just features
7. **Mobile view** — open DevTools device mode and screenshot the sidebar closed + chat open — shows responsive design

**Tips:**
- Use a dark screenshot tool (Screenpresso, ShareX, or browser DevTools) for consistency
- Crop to the visible content area — don't include browser chrome unless it adds context
- For GitHub README, use 1200×630 images for the hero screenshot (standard Open Graph size)

---

## Interview Talking Points

**"Walk me through your project architecture."**
"I used Flask's application factory pattern — `create_app()` returns the app with all blueprints registered. There are three blueprints: `chat_bp` for AI conversation and tool shortcuts, `tools_bp` for REST API endpoints, and `admin_bp` for the analytics dashboard. The AI service is abstracted behind a thin service layer that handles provider selection and wraps API errors into a custom exception hierarchy."

**"What was the hardest part to build?"**
"The phishing and scam detectors. I had to research real attack patterns and translate them into weighted heuristic checks that produce meaningful risk scores. It's not just keyword matching — for example, brand impersonation detection has to distinguish `apple.com` (legitimate) from `apple-login-verify.net` (impersonation) using domain parsing and position checks."

**"How did you handle the case where the AI API is down?"**
"I have a custom exception hierarchy — `AIQuotaError`, `AIAuthError`, `AIConnectionError` — each returns a different error message to the frontend. The JS then renders a service notice that explains what's wrong and tells the user the security tools still work without the AI. The tool-only path uses no external API at all."

**"How would you scale this?"**
"The main bottleneck would be SQLite under concurrent writes. I'd swap it for PostgreSQL with connection pooling. For the AI, the rate limiter is currently in-memory which breaks under multiple Gunicorn workers — I'd move that to Redis. The heuristic scanners are stateless and scale horizontally without changes."

**"What would you add next?"**
"A breach exposure checker using the HIBP API (Have I Been Pwned), which would tell users if their email appears in known data breaches. I'd also add a PDF export of the security session report, and potentially a dark/light theme toggle."
