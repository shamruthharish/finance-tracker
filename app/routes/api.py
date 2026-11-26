
import time

from flask import Blueprint, jsonify, current_app

api_bp = Blueprint("api", __name__)

# Record application startup time
START_TIME = time.time()


@api_bp.route("/api/health", methods=["GET"])
def health_check():
    """Return application health and uptime."""

    uptime = int(time.time() - START_TIME)

    return jsonify({
        "status": "healthy",
        "uptime_seconds": uptime
    }), 200
