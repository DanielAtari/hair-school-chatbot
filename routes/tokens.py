# routes/tokens.py
from flask import Blueprint, request, jsonify
from database.models import db, TokenUsageLog
from datetime import datetime

tokens_bp = Blueprint("tokens", __name__)

@tokens_bp.route("/update_tokens", methods=["POST"])
def update_tokens():
    data = request.get_json()
    business_id = data.get("business_id")
    month = data.get("month")
    tokens_used = data.get("tokens_used")

    log = TokenUsageLog.query.filter_by(business_id=business_id, month=month).first()
    if not log:
        log = TokenUsageLog(business_id=business_id, month=month, total_tokens=0)

    log.total_tokens += tokens_used
    log.updated_at = datetime.utcnow()

    db.session.add(log)
    db.session.commit()

    return jsonify({"status": "ok", "total_tokens": log.total_tokens})
