import logging
from flask import Blueprint, request, jsonify, session
from services.ai_service import get_ai_response, AIQuotaError, AIAuthError, AIConnectionError
from simulators.password_checker import check_password_strength
from simulators.phishing_detector import analyze_phishing
from simulators.scam_detector import analyze_scam
from simulators.url_checker import analyze_url
from utils.sanitizer import sanitize_input
from utils.rate_limiter import rate_limit
from database.db import log_tool_usage, save_message

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)


@chat_bp.route("/chat", methods=["POST"])
@rate_limit(max_requests=40, window_seconds=60)
def chat():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid request body."}), 400

        raw = data.get("message", "")
        user_message = sanitize_input(raw, max_length=2000)

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        # ── Specialised tool triggers ─────────────────────────────────────
        lower = user_message.lower()

        if lower.startswith("password:"):
            pw = user_message[9:].strip()
            if not pw:
                return jsonify({"error": "Please provide a password after 'password:'."}), 400
            result = check_password_strength(pw)
            log_tool_usage("password_checker")
            return jsonify({"reply": result["formatted"], "tool": "password", "data": result})

        if lower.startswith("phish:"):
            email_text = user_message[6:].strip()
            if not email_text:
                return jsonify({"error": "Please provide email text after 'phish:'."}), 400
            result = analyze_phishing(email_text)
            log_tool_usage("phishing_detector")
            return jsonify({"reply": result["formatted"], "tool": "phishing", "data": result})

        if lower.startswith("scam:"):
            text = user_message[5:].strip()
            if not text:
                return jsonify({"error": "Please provide text after 'scam:'."}), 400
            result = analyze_scam(text)
            log_tool_usage("scam_detector")
            return jsonify({"reply": result["formatted"], "tool": "scam", "data": result})

        if lower.startswith("url:"):
            url_input = user_message[4:].strip()
            if not url_input:
                return jsonify({"error": "Please provide a URL after 'url:'."}), 400
            result = analyze_url(url_input)
            log_tool_usage("url_checker")
            return jsonify({"reply": result["formatted"], "tool": "url", "data": result})

        # ── Standard AI conversation ──────────────────────────────────────
        if "conversation_history" not in session:
            session["conversation_history"] = []

        history = session["conversation_history"]
        history.append({"role": "user", "content": user_message})

        recent = history[-20:]
        reply = get_ai_response(recent)

        history.append({"role": "assistant", "content": reply})
        session["conversation_history"] = history

        save_message("user", user_message)
        save_message("assistant", reply)

        return jsonify({"reply": reply})

    except AIQuotaError:
        return jsonify({
            "error": "ai_quota",
            "message": (
                "The AI assistant is temporarily unavailable — the OpenAI API quota has been reached. "
                "The Security Tools (Password Analyzer, Phishing Detector, Scam Detector) still work normally. "
                "To restore AI chat, add credits at platform.openai.com/account/billing."
            )
        }), 503

    except AIAuthError:
        return jsonify({
            "error": "ai_auth",
            "message": "AI service authentication failed. Please verify the OPENAI_API_KEY in your .env file."
        }), 503

    except AIConnectionError:
        return jsonify({
            "error": "ai_connection",
            "message": "Could not reach the AI service. Please check your internet connection and try again."
        }), 503

    except RuntimeError as exc:
        logger.error("Configuration error: %s", exc)
        return jsonify({"error": "config", "message": str(exc)}), 500

    except Exception as exc:
        logger.error("Chat endpoint error: %s", exc, exc_info=True)
        return jsonify({"error": "server", "message": "An unexpected error occurred. Please try again."}), 500


@chat_bp.route("/reset", methods=["POST"])
def reset():
    session["conversation_history"] = []
    return jsonify({"status": "Conversation reset successfully."})
