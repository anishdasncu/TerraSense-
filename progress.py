from flask import Blueprint, jsonify
from db import footprint_history

progress_bp = Blueprint("progress", __name__)


@progress_bp.route("/api/progress/<user_id>")
def get_progress(user_id):
    if footprint_history is None:
        return jsonify([])

    records = list(
        footprint_history
        .find({"user_id": user_id}, {"_id": 0})
        .sort("submitted_at", 1)  
    )
    return jsonify(records)
