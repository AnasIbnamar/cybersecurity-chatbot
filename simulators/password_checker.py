import re
import secrets
import string


def check_password_strength(password: str) -> dict:
    score = 0
    feedback = []
    suggestions = []

    length = len(password)
    if length >= 16:
        score += 3
        feedback.append({"status": "good", "text": f"Excellent length ({length} characters)"})
    elif length >= 12:
        score += 2
        feedback.append({"status": "good", "text": f"Good length ({length} characters)"})
    elif length >= 8:
        score += 1
        feedback.append({"status": "warn", "text": f"Acceptable length ({length} chars) — 12+ recommended"})
        suggestions.append("Use at least 12 characters for stronger security")
    else:
        feedback.append({"status": "bad", "text": f"Too short ({length} characters) — minimum 8 required"})
        suggestions.append("Use at least 8 characters (12+ strongly recommended)")

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|`~]', password))

    if has_upper:
        score += 1
        feedback.append({"status": "good", "text": "Contains uppercase letters (A–Z)"})
    else:
        feedback.append({"status": "bad", "text": "Missing uppercase letters (A–Z)"})
        suggestions.append("Add uppercase letters (A–Z)")

    if has_lower:
        score += 1
        feedback.append({"status": "good", "text": "Contains lowercase letters (a–z)"})
    else:
        feedback.append({"status": "bad", "text": "Missing lowercase letters (a–z)"})
        suggestions.append("Add lowercase letters (a–z)")

    if has_digit:
        score += 1
        feedback.append({"status": "good", "text": "Contains numbers (0–9)"})
    else:
        feedback.append({"status": "bad", "text": "Missing numbers (0–9)"})
        suggestions.append("Include at least one number (0–9)")

    if has_special:
        score += 2
        feedback.append({"status": "good", "text": "Contains special characters"})
    else:
        feedback.append({"status": "bad", "text": "No special characters (!@#$%^&* etc.)"})
        suggestions.append("Add special characters such as !@#$%^&*")

    common = [
        'password', '123456', 'qwerty', 'abc123', 'admin', 'letmein',
        'welcome', 'monkey', 'dragon', 'master', '111111', 'pass', 'login',
        'iloveyou', 'sunshine', 'princess',
    ]
    pw_lower = password.lower()
    if any(p in pw_lower for p in common):
        score -= 2
        feedback.append({"status": "bad", "text": "Contains a common word or pattern"})
        suggestions.append("Avoid dictionary words and well-known patterns")

    if re.search(r'(.)\1{2,}', password):
        score -= 1
        feedback.append({"status": "warn", "text": "Contains repeated characters (e.g. 'aaa')"})
        suggestions.append("Avoid repeating the same character consecutively")

    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)', pw_lower):
        score -= 1
        feedback.append({"status": "warn", "text": "Contains sequential characters (e.g. '123', 'abc')"})
        suggestions.append("Avoid sequential patterns like '123' or 'abc'")

    score = max(0, score)

    if score >= 8:
        strength, level, color = "Very Strong", 5, "#00c853"
    elif score >= 6:
        strength, level, color = "Strong", 4, "#64dd17"
    elif score >= 4:
        strength, level, color = "Moderate", 3, "#ffd600"
    elif score >= 2:
        strength, level, color = "Weak", 2, "#ff6d00"
    else:
        strength, level, color = "Very Weak", 1, "#d50000"

    return {
        "strength": strength,
        "level": level,
        "score": score,
        "max_score": 9,
        "feedback": feedback,
        "suggestions": suggestions,
        "color": color,
        "formatted": _build_text_report(strength, score, feedback, suggestions),
    }


def _build_text_report(strength: str, score: int, feedback: list, suggestions: list) -> str:
    markers = {"good": "[Pass]", "warn": "[Warn]", "bad": "[Fail]"}
    lines = [
        f"**Password Strength: {strength}** — Score {score}/9",
        "",
        "**Analysis**",
    ]
    for item in feedback:
        lines.append(f"{markers.get(item['status'], '[Info]')} {item['text']}")

    if suggestions:
        lines += ["", "**Recommendations**"]
        for s in suggestions:
            lines.append(f"- {s}")

    lines += [
        "",
        "**Note:** Use a password manager such as Bitwarden or 1Password to generate and store unique passwords for every account.",
    ]
    return "\n".join(lines)


def generate_password(length: int = 16) -> str:
    length = max(12, min(64, length))
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    # Guarantee at least one of each character class
    guaranteed = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+[]{}|;:,.<>?"),
    ]
    rest = [secrets.choice(alphabet) for _ in range(length - 4)]
    pool = guaranteed + rest
    secrets.SystemRandom().shuffle(pool)
    return "".join(pool)
