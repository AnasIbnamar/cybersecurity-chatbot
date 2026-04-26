import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

_DB_PATH = os.getenv("DATABASE_PATH", "cyberguard.db")


def _get_conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                role       TEXT    NOT NULL,
                content    TEXT    NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tool_usage (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name  TEXT    NOT NULL,
                used_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS exports (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                filename   TEXT    NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logger.info("Database initialised")
    except Exception as exc:
        logger.error("Database init failed: %s", exc)
    finally:
        conn.close()


def save_message(role: str, content: str) -> None:
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content[:5000])
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("save_message failed: %s", exc)


def log_tool_usage(tool_name: str) -> None:
    try:
        conn = _get_conn()
        conn.execute("INSERT INTO tool_usage (tool_name) VALUES (?)", (tool_name,))
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("log_tool_usage failed: %s", exc)


def log_export(filename: str) -> None:
    try:
        conn = _get_conn()
        conn.execute("INSERT INTO exports (filename) VALUES (?)", (filename,))
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("log_export failed: %s", exc)


def get_tool_stats() -> dict:
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT tool_name, COUNT(*) AS cnt FROM tool_usage GROUP BY tool_name"
        ).fetchall()
        conn.close()
        return {r["tool_name"]: r["cnt"] for r in rows}
    except Exception:
        return {}


def get_admin_stats() -> dict:
    try:
        conn = _get_conn()

        total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        user_messages  = conn.execute("SELECT COUNT(*) FROM messages WHERE role = 'user'").fetchone()[0]
        ai_responses   = conn.execute("SELECT COUNT(*) FROM messages WHERE role = 'assistant'").fetchone()[0]
        total_scans    = conn.execute("SELECT COUNT(*) FROM tool_usage").fetchone()[0]

        tool_rows = conn.execute(
            "SELECT tool_name, COUNT(*) AS cnt FROM tool_usage GROUP BY tool_name ORDER BY cnt DESC"
        ).fetchall()
        tool_counts = {r["tool_name"]: r["cnt"] for r in tool_rows}
        top_tool    = tool_rows[0]["tool_name"].replace("_", " ").title() if tool_rows else "—"

        recent_rows = conn.execute(
            "SELECT tool_name, used_at FROM tool_usage ORDER BY used_at DESC LIMIT 20"
        ).fetchall()
        recent_activity = [{"tool": r["tool_name"], "at": r["used_at"]} for r in recent_rows]

        daily_rows = conn.execute("""
            SELECT DATE(used_at) AS day, COUNT(*) AS cnt
            FROM tool_usage
            WHERE used_at >= DATE('now', '-6 days')
            GROUP BY DATE(used_at)
            ORDER BY day DESC
        """).fetchall()
        daily_stats = [{"day": r["day"], "count": r["cnt"]} for r in daily_rows]

        conn.close()
        return {
            "total_messages":  total_messages,
            "user_messages":   user_messages,
            "ai_responses":    ai_responses,
            "total_scans":     total_scans,
            "tool_counts":     tool_counts,
            "top_tool":        top_tool,
            "recent_activity": recent_activity,
            "daily_stats":     daily_stats,
        }
    except Exception as exc:
        logger.warning("get_admin_stats failed: %s", exc)
        return {
            "total_messages":  0,
            "user_messages":   0,
            "ai_responses":    0,
            "total_scans":     0,
            "tool_counts":     {},
            "top_tool":        "—",
            "recent_activity": [],
            "daily_stats":     [],
        }
