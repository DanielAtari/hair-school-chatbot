from flask import Blueprint, request, render_template
from database.models import db, Message

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/conversations/<int:business_id>")
def view_conversations(business_id):
    query = request.args.get("q", "").strip()
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    q = db.session.query(Message).filter_by(business_id=business_id)

    if query:
        q = q.filter(Message.content.ilike(f"%{query}%"))

    if from_date:
        q = q.filter(Message.timestamp >= from_date)
    if to_date:
        q = q.filter(Message.timestamp <= to_date)

    messages = q.order_by(Message.timestamp.desc()).limit(100).all()

    return render_template("conversations.html", messages=messages, business_id=business_id)
