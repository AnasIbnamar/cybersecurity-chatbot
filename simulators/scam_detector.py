import re

_PATTERNS: dict[str, int] = {
    "you have won": 3,
    "you won": 3,
    "you've been selected": 2,
    "congratulations": 1,
    "prize winner": 3,
    "lottery winner": 4,
    "sweepstakes": 3,
    "lucky winner": 3,
    "unclaimed funds": 3,
    "inheritance": 4,
    "nigerian prince": 5,
    "transfer funds": 3,
    "send money": 4,
    "wire transfer": 3,
    "western union": 4,
    "moneygram": 4,
    "gift card": 3,
    "itunes card": 4,
    "google play card": 4,
    "amazon gift card": 4,
    "guaranteed returns": 3,
    "risk-free investment": 3,
    "double your money": 4,
    "get rich quick": 4,
    "investment opportunity": 2,
    "bitcoin investment": 3,
    "work from home": 2,
    "secret shopper": 3,
    "easy money": 3,
    "make money fast": 3,
    "no experience needed": 2,
    "100% free": 2,
    "claim your prize": 3,
    "claim now": 2,
    "act now": 2,
    "expires today": 2,
    "limited time": 1,
    "free gift": 2,
}

_SENSITIVE_REQUESTS: list[tuple[str, str]] = [
    ("social security", "Social Security Number (SSN)"),
    ("ssn", "SSN"),
    ("bank account", "bank account number"),
    ("routing number", "bank routing number"),
    ("credit card", "credit card number"),
    ("pin number", "PIN"),
    ("password", "account password"),
    ("date of birth", "date of birth"),
    ("mother maiden", "mother's maiden name"),
]

_MONEY_RE = re.compile(r'\$[\d,]+|\b\d[\d,]*\s*(million|billion|thousand)\b', re.IGNORECASE)
_URGENCY_RE = re.compile(r'\b(immediately|asap|urgent|expires|deadline|act now|respond now)\b', re.IGNORECASE)


def analyze_scam(text: str) -> dict:
    indicators = []
    scam_score = 0
    text_lower = text.lower()

    for pattern, weight in _PATTERNS.items():
        if pattern in text_lower:
            sev = "high" if weight >= 3 else "medium"
            indicators.append({"severity": sev, "text": f'Contains scam phrase: "{pattern}"'})
            scam_score += weight

    for term, label in _SENSITIVE_REQUESTS:
        if term in text_lower:
            indicators.append({"severity": "critical", "text": f"Requests your {label} — NEVER share this with anyone"})
            scam_score += 5
            break

    if _MONEY_RE.search(text_lower):
        indicators.append({"severity": "medium", "text": "Mentions a large sum of money — a hallmark of financial scams"})
        scam_score += 2

    if _URGENCY_RE.search(text):
        indicators.append({"severity": "medium", "text": "Applies urgency/pressure tactics to rush your decision"})
        scam_score += 2

    scam_score = min(scam_score, 10)

    if scam_score >= 7:
        verdict, risk_level = "HIGH RISK — Very Likely a Scam", "high"
        recommendation = (
            "Do NOT respond, send money, or share any personal information. "
            "Block the sender and report the message as spam. "
            "If you have already sent money, contact your bank immediately to attempt a reversal."
        )
    elif scam_score >= 4:
        verdict, risk_level = "MEDIUM RISK — Suspicious Content", "medium"
        recommendation = (
            "Research the company or person independently before taking any action. "
            "Never send money or provide financial/personal information to unverified sources."
        )
    elif scam_score >= 1:
        verdict, risk_level = "LOW RISK — Proceed with Caution", "low"
        recommendation = (
            "Some warning signs detected. Verify the source independently "
            "before responding or providing any information."
        )
    else:
        verdict, risk_level = "No Scam Indicators Detected", "safe"
        recommendation = (
            "No scam patterns detected in this text. "
            "Always verify unusual requests through official channels."
        )

    return {
        "verdict": verdict,
        "risk_level": risk_level,
        "scam_score": scam_score,
        "indicators": indicators[:6],
        "recommendation": recommendation,
        "formatted": _build_text_report(verdict, scam_score, indicators, recommendation, risk_level),
    }


def _build_text_report(verdict, scam_score, indicators, recommendation, risk_level) -> str:
    sev_labels = {"critical": "[Critical]", "high": "[High]", "medium": "[Medium]", "low": "[Low]"}

    lines = [
        "**Scam Detection Analysis**",
        "",
        f"**Verdict:** {verdict}",
        f"**Risk Score:** {scam_score}/10",
    ]
    if indicators:
        lines += ["", "**Warning Signs Detected:**"]
        for ind in indicators[:5]:
            label = sev_labels.get(ind['severity'], '[Info]')
            lines.append(f"{label} {ind['text']}")
    lines += ["", "**Recommendation:**", recommendation]
    return "\n".join(lines)
