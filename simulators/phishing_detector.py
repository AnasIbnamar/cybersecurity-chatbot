import re

_KEYWORDS: dict[str, int] = {
    "verify your account": 3,
    "confirm your identity": 3,
    "account suspended": 3,
    "account has been locked": 3,
    "update your payment": 3,
    "unusual login activity": 3,
    "unauthorized access detected": 3,
    "your account will be closed": 3,
    "immediate action required": 3,
    "security alert": 2,
    "suspicious activity": 2,
    "click here": 2,
    "urgent": 2,
    "dear customer": 2,
    "dear user": 2,
    "dear account holder": 2,
    "dear member": 2,
    "billing information": 2,
    "invoice attached": 2,
    "your password has expired": 2,
    "limited time offer": 1,
    "act now": 2,
    "paypal": 2,
    "amazon security": 2,
    "netflix account": 2,
    "microsoft account": 2,
    "apple id": 2,
    "irs": 2,
    "bank of america": 2,
    "wire transfer": 1,
    "gift card": 2,
    "enter your credentials": 2,
}

_URGENCY_RE = re.compile(
    r'\bimmediately\b|'
    r'\basap\b|'
    r'within\s+\d+\s+hour|'
    r'within\s+24|'
    r'within\s+48|'
    r'account will be (closed|suspended|deleted|terminated)|'
    r'respond within|'
    r'last warning|'
    r'final notice|'
    r'expires in \d',
    re.IGNORECASE
)

_SENSITIVE_RE = re.compile(
    r'\bpassword\b|\bpin\b|\bssn\b|social security|'
    r'bank account|routing number|credit card|'
    r'date of birth|mother.s maiden',
    re.IGNORECASE
)

_SHORT_URL_RE = re.compile(
    r'bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly|is\.gd|buff\.ly',
    re.IGNORECASE
)

_SPOOF_URL_RE = re.compile(
    r'secure-.*\.(com|net|org)|'
    r'.*-update\.(com|net)|'
    r'.*-verify\.(com|net)|'
    r'.*-support\.(com|net)|'
    r'.*-login\.(com|net)',
    re.IGNORECASE
)


def analyze_phishing(text: str) -> dict:
    indicators = []
    risk_score = 0
    text_lower = text.lower()

    for kw, weight in _KEYWORDS.items():
        if kw in text_lower:
            sev = "high" if weight >= 3 else "medium" if weight == 2 else "low"
            indicators.append({"severity": sev, "text": f'Contains phrase: "{kw}"'})
            risk_score += weight

    if _URGENCY_RE.search(text):
        indicators.append({"severity": "high", "text": "Creates artificial urgency to pressure the recipient"})
        risk_score += 3

    urls = re.findall(r'https?://[^\s<>"\']+', text)
    if urls:
        indicators.append({"severity": "medium", "text": f"Contains {len(urls)} link(s) — hover to verify before clicking"})
        risk_score += 2
        for url in urls:
            if _SHORT_URL_RE.search(url):
                indicators.append({"severity": "high", "text": "Uses a shortened URL — hides the real destination"})
                risk_score += 3
                break
            if _SPOOF_URL_RE.search(url):
                indicators.append({"severity": "high", "text": "Link domain pattern matches known spoofing techniques"})
                risk_score += 3
                break

    generic_greetings = ["dear customer", "dear user", "dear account holder", "dear member", "hello dear"]
    if any(g in text_lower for g in generic_greetings):
        indicators.append({"severity": "medium", "text": "Generic greeting — legitimate companies address you by name"})
        risk_score += 2

    if _SENSITIVE_RE.search(text):
        indicators.append({"severity": "high", "text": "Requests sensitive credentials or personal data — legitimate services never ask via email"})
        risk_score += 4

    risk_score = min(risk_score, 10)

    if risk_score >= 7:
        verdict, risk_level = "HIGH RISK — Likely Phishing", "high"
        recommendation = (
            "Do NOT click any links or open attachments. Delete this email immediately. "
            "If you believe your account may be affected, go directly to the official website "
            "(type the URL yourself) and change your password. "
            "Report the email as phishing to your email provider."
        )
    elif risk_score >= 4:
        verdict, risk_level = "MEDIUM RISK — Suspicious Email", "medium"
        recommendation = (
            "Verify the sender's email domain carefully — it may be spoofed. "
            "Do not click links in the email; instead, navigate directly to the company's official website. "
            "Contact the company through official support channels to confirm."
        )
    elif risk_score >= 1:
        verdict, risk_level = "LOW RISK — Proceed with Caution", "low"
        recommendation = (
            "A few minor indicators were detected. Verify the sender's identity "
            "and confirm any request is legitimate before taking action."
        )
    else:
        verdict, risk_level = "No Phishing Indicators Detected", "safe"
        recommendation = (
            "No obvious phishing patterns found. Always verify the sender before "
            "sharing personal information or clicking unexpected links."
        )

    return {
        "verdict": verdict,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "indicators": indicators[:6],
        "recommendation": recommendation,
        "formatted": _build_text_report(verdict, risk_score, indicators, recommendation, risk_level),
    }


def _build_text_report(verdict, risk_score, indicators, recommendation, risk_level) -> str:
    sev_labels = {"high": "[High]", "medium": "[Medium]", "low": "[Low]"}

    lines = [
        "**Phishing Analysis Result**",
        "",
        f"**Verdict:** {verdict}",
        f"**Risk Score:** {risk_score}/10",
    ]
    if indicators:
        lines += ["", "**Red Flags Detected**"]
        for ind in indicators[:5]:
            label = sev_labels.get(ind['severity'], '[Info]')
            lines.append(f"{label} {ind['text']}")
    lines += ["", "**Recommendation**", recommendation]
    return "\n".join(lines)
