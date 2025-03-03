import logging
import os
from flask import Flask, jsonify
from sqlalchemy import text
from config import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set default port if not provided
port_number = int(os.getenv("APP_PORT", 5153))

@app.route("/health_check")
def health_check():
    return "ok"

@app.route("/readiness_check")
def readiness_check():
    try:
        count = db.session.execute(text("SELECT COUNT(*) FROM tokens")).scalar()
        return "ok"
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return jsonify({"error": "failed"}), 500
    finally:
        db.session.close()

def get_daily_visits():
    """Fetches daily visit counts from the database."""
    with app.app_context():
        try:
            result = db.session.execute(text("""
                SELECT DATE(created_at) AS date, COUNT(*) AS visits
                FROM tokens
                WHERE used_at IS NOT NULL
                GROUP BY DATE(created_at)
            """))

            response = {str(row[0]): row[1] for row in result}
            logger.info(f"Daily visits: {response}")
            return response
        except Exception as e:
            logger.error(f"Error fetching daily visits: {e}")
            return {}
        finally:
            db.session.close()

@app.route("/api/reports/daily_usage", methods=["GET"])
def daily_visits():
    return jsonify(get_daily_visits())

@app.route("/api/reports/user_visits", methods=["GET"])
def all_user_visits():
    try:
        result = db.session.execute(text("""
            SELECT t.user_id, COUNT(*) AS visits, u.joined_at
            FROM tokens t
            JOIN users u ON t.user_id = u.id
            GROUP BY t.user_id, u.joined_at
        """))

        visits = [{"user_id": row[0], "visits": row[1], "joined_at": row[2]} for row in result]
        return jsonify(visits)
    except Exception as e:
        logger.error(f"Error fetching user visits: {e}")
        return jsonify({"error": "Failed to fetch user visits"}), 500
    finally:
        db.session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_number, debug=True)

