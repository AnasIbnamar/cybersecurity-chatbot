import logging
from flask import Blueprint, request, jsonify
from simulators.password_checker import check_password_strength, generate_password
from simulators.phishing_detector import analyze_phishing
from simulators.scam_detector import analyze_scam
from simulators.url_checker import analyze_url
from utils.sanitizer import sanitize_input
from utils.rate_limiter import rate_limit
from database.db import log_tool_usage, get_tool_stats

tools_bp = Blueprint("tools", __name__)
logger = logging.getLogger(__name__)


@tools_bp.route("/api/password-check", methods=["POST"])
@rate_limit(max_requests=30, window_seconds=60)
def password_check():
    data = request.get_json(silent=True) or {}
    password = sanitize_input(data.get("password", ""), max_length=200)
    if not password:
        return jsonify({"error": "Password is required."}), 400
    result = check_password_strength(password)
    log_tool_usage("password_checker")
    return jsonify(result)


@tools_bp.route("/api/generate-password", methods=["POST"])
@rate_limit(max_requests=30, window_seconds=60)
def gen_password():
    data = request.get_json(silent=True) or {}
    try:
        length = int(data.get("length", 16))
    except (ValueError, TypeError):
        length = 16
    length = max(12, min(64, length))
    pw = generate_password(length)
    return jsonify({"password": pw, "length": length})


@tools_bp.route("/api/phishing-check", methods=["POST"])
@rate_limit(max_requests=20, window_seconds=60)
def phishing_check():
    data = request.get_json(silent=True) or {}
    text = sanitize_input(data.get("text", ""), max_length=3000)
    if not text:
        return jsonify({"error": "Email text is required."}), 400
    result = analyze_phishing(text)
    log_tool_usage("phishing_detector")
    return jsonify(result)


@tools_bp.route("/api/scam-check", methods=["POST"])
@rate_limit(max_requests=20, window_seconds=60)
def scam_check():
    data = request.get_json(silent=True) or {}
    text = sanitize_input(data.get("text", ""), max_length=3000)
    if not text:
        return jsonify({"error": "Message text is required."}), 400
    result = analyze_scam(text)
    log_tool_usage("scam_detector")
    return jsonify(result)


@tools_bp.route("/api/url-check", methods=["POST"])
@rate_limit(max_requests=20, window_seconds=60)
def url_check():
    data = request.get_json(silent=True) or {}
    url = sanitize_input(data.get("url", ""), max_length=2000)
    if not url:
        return jsonify({"error": "URL is required."}), 400
    result = analyze_url(url)
    log_tool_usage("url_checker")
    return jsonify(result)


@tools_bp.route("/api/stats", methods=["GET"])
def stats():
    return jsonify(get_tool_stats())
