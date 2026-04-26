import os
from flask import Flask, render_template, session
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    from config import get_config
    app.config.from_object(get_config())

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not groq_key and not openai_key:
        raise RuntimeError(
            "No AI API key configured. "
            "Add GROQ_API_KEY (free at console.groq.com) "
            "or OPENAI_API_KEY to your .env file."
        )

    from utils.logger import setup_logger
    setup_logger(app)

    from database.db import init_db
    with app.app_context():
        init_db()

    from routes.chat import chat_bp
    from routes.tools import tools_bp
    from routes.admin import admin_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/dashboard")
    def dashboard():
        if "conversation_history" not in session:
            session["conversation_history"] = []
        return render_template("index.html")

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Internal server error"}, 500

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
