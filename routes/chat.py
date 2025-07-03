from flask import Blueprint, render_template, request, jsonify
from services.chat_service import chatbot
from database.models import db, Message
from datetime import timedelta, datetime
import os
from werkzeug.utils import secure_filename

chat_bp = Blueprint("chat", __name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "txt"}

def to_israel_time(dt):
    if dt is None:
        return ""
    return (dt + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_bp.route("/chat/<int:business_id>", methods=["GET"])
def chat_interface(business_id):
    return render_template("chat.html", business_id=business_id)

@chat_bp.route("/chat/<int:business_id>/ask", methods=["POST"])
def ask_question(business_id):
    question = request.form.get("question", "").strip()
    files = request.files.getlist("files")

    answer = chatbot(business_id, question) if question else ""

    try:
        # שמירת טקסט שאלה ותשובה
        if question and answer:
            db.session.add(Message(business_id=business_id, role="user", content=question, timestamp=datetime.utcnow()))
            db.session.add(Message(business_id=business_id, role="assistant", content=answer, timestamp=datetime.utcnow()))

        # שמירת קבצים
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder_path = os.path.join(UPLOAD_FOLDER, str(business_id))
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)

                # שמירה כהודעה חדשה
                db.session.add(Message(
                    business_id=business_id,
                    role="user",
                    content=f"/uploads/{business_id}/{filename}",
                    timestamp=datetime.utcnow(),
                    message_type="file"
                ))

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("⚠️ Database Error (saving messages):", e)

    return jsonify({"answer": answer})

@chat_bp.route("/chat/<int:business_id>/history", methods=["GET"])
def get_history(business_id):
    history_objs = (
        db.session.query(Message)
        .filter_by(business_id=business_id)
        .order_by(Message.timestamp.desc())
        .limit(10)
        .all()
    )[::-1]

    history = []
    for msg in history_objs:
        role = msg.role
        if role == "bot":
            role = "assistant"
        elif role not in ["user", "assistant"]:
            continue

        history.append({
            "role": role,
            "content": msg.content,
            "type": getattr(msg, "message_type", "text"),
            "timestamp": to_israel_time(msg.timestamp)
        })

    return jsonify({"messages": history})