import logging
from flask import Blueprint, render_template
from database.db import get_admin_stats

admin_bp = Blueprint("admin", __name__)
logger = logging.getLogger(__name__)


@admin_bp.route("/admin")
def admin_dashboard():
    stats = get_admin_stats()
    total = stats["total_scans"] or 1
    tool_pcts = {k: round(v / total * 100) for k, v in stats["tool_counts"].items()}
    return render_template("admin.html", stats=stats, tool_pcts=tool_pcts)
