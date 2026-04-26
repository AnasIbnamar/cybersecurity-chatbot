import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

_client: OpenAI | None = None

SYSTEM_PROMPT = """You are CyberGuard, a professional AI cybersecurity assistant.

Your role is to provide accurate, practical, and actionable cybersecurity guidance to users at every skill level — from complete beginners to experienced IT professionals.

## What you do
- Answer cybersecurity questions clearly and accurately
- Analyze threats and explain real-world risks
- Guide users through protecting accounts, devices, networks, and data
- Assist with security incident response and recovery steps
- Explain complex security concepts in plain, accessible language
- Provide step-by-step, hands-on security advice

## Topics you cover
- Password hygiene, MFA, and account security
- Phishing, spear-phishing, vishing, and social engineering
- Malware, ransomware, spyware, and threat detection
- Network security, Wi-Fi safety, and firewall basics
- VPNs, DNS security, and encrypted communications
- Two-factor / multi-factor authentication (2FA / MFA)
- Privacy, data protection, and GDPR awareness
- Cloud security and safe data storage
- Mobile device security and app safety
- Data breaches — response, recovery, and prevention
- Safe browsing, browser hardening, and ad blockers
- Identity theft prevention and recovery
- Corporate security awareness and Zero Trust principles
- Incident response frameworks (NIST, SANS)

## Tone and style
- Professional, direct, and trustworthy — like a senior security consultant
- Adapt complexity to the user: simple language for beginners, technical depth for experts
- Use numbered steps for procedures and bullet points for lists
- Be concise but thorough — prioritise actionable advice over theory
- Never be condescending; every question deserves a complete answer
- When a situation is severe (e.g. active breach), clearly state urgency and escalation path

## Absolute rules
- Never assist with offensive hacking, unauthorised access, or surveillance
- Never provide instructions that could enable harm to others
- Always recommend professional incident response help for active breaches
- When uncertain, say so and direct users to authoritative sources (CISA, NIST, NCSC)
- Prioritise user safety, privacy, and data protection in every response

Respond in 150–400 words unless a detailed step-by-step guide is explicitly needed. Use markdown formatting (bold, lists, code blocks) where it improves clarity."""


# ── Provider detection ────────────────────────────────────────────────────────
# Priority: GROQ_API_KEY → OPENAI_API_KEY
# Groq is OpenAI-compatible so we reuse the same SDK — just a different base_url.

_PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model":    "llama-3.3-70b-versatile",
        "env_var":  "GROQ_API_KEY",
    },
    "openai": {
        "base_url": None,           # uses the SDK default
        "model":    "gpt-4o-mini",
        "env_var":  "OPENAI_API_KEY",
    },
}

_client: OpenAI | None = None
_active_model: str = ""


class AIQuotaError(Exception):
    """Raised when the API account has no remaining quota."""

class AIAuthError(Exception):
    """Raised when the API key is invalid or missing."""

class AIConnectionError(Exception):
    """Raised when the AI service is unreachable."""


def _get_client() -> tuple[OpenAI, str]:
    """Return (client, model_name), auto-selecting the first configured provider."""
    global _client, _active_model
    if _client is not None:
        return _client, _active_model

    for name, cfg in _PROVIDERS.items():
        key = os.getenv(cfg["env_var"], "").strip()
        if not key:
            continue
        kwargs: dict = {"api_key": key}
        if cfg["base_url"]:
            kwargs["base_url"] = cfg["base_url"]
        _client = OpenAI(**kwargs)
        _active_model = cfg["model"]
        logger.info("AI provider: %s  model: %s", name, _active_model)
        return _client, _active_model

    raise RuntimeError(
        "No AI API key found. "
        "Add GROQ_API_KEY (free at console.groq.com) "
        "or OPENAI_API_KEY to your .env file."
    )


def get_ai_response(conversation_history: list) -> str:
    from openai import RateLimitError, AuthenticationError, APIConnectionError, APIStatusError

    try:
        client, model = _get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history,
            ],
            max_tokens=700,
            temperature=0.35,
        )
        return response.choices[0].message.content

    except AuthenticationError as exc:
        logger.error("AI authentication failed: %s", exc)
        raise AIAuthError(
            "API key rejected. Check that your GROQ_API_KEY (or OPENAI_API_KEY) "
            "in .env is correct and not expired."
        ) from exc

    except RateLimitError as exc:
        msg = str(exc).lower()
        if "insufficient_quota" in msg or "exceeded your current quota" in msg:
            logger.warning("AI quota exceeded: %s", exc)
            raise AIQuotaError(
                "API quota reached. If you are using OpenAI, add credits at "
                "platform.openai.com/account/billing. "
                "For a free alternative, sign up at console.groq.com and add "
                "GROQ_API_KEY to your .env file."
            ) from exc
        logger.warning("AI rate limited: %s", exc)
        raise AIQuotaError("Rate limit reached — please wait a moment and try again.") from exc

    except APIConnectionError as exc:
        logger.error("AI connection error: %s", exc)
        raise AIConnectionError("Could not reach the AI service. Check your internet connection.") from exc

    except APIStatusError as exc:
        logger.error("AI API status error %s: %s", exc.status_code, exc)
        raise

    except Exception as exc:
        logger.error("AI unexpected error: %s", exc, exc_info=True)
        raise
