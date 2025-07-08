import uuid
from datetime import datetime
from flask import Blueprint, session, redirect, url_for, flash
from chromadb import PersistentClient
from database.models import Bot, db  # ודא שיש לך את המודל המתאים במסד שלך
import os

bot_creation_bp = Blueprint("bot_creation", __name__)

chroma_client = PersistentClient(path="chroma_db/master")

@bot_creation_bp.route("/create-bot", methods=["GET", "POST"])
def create_bot():
    user_id = session.get("user_id")
    if not user_id:
        flash("אנא התחבר לפני יצירת בוט.")
        return redirect(url_for("auth.login"))  # שנה לכתובת המתאימה

    # יצירת מזהה ייחודי לבוט חדש
    bot_id = str(uuid.uuid4())

    try:
        # יצירת קולקשן חדש ב-Chroma בשם ייחודי
        new_collection = chroma_client.get_or_create_collection(bot_id)

        # נטען את המידע שהועלה לאישור מה־session (רק אחרי אישור במאסטר)
        uploaded_files = session.get("uploaded_files_pending", [])
        raw_texts = session.get("raw_text_summaries_pending", [])

        # טען את כל הטקסטים לקולקשן החדש
        for text in uploaded_files + raw_texts:
            doc_id = str(uuid.uuid4())
            new_collection.add(documents=[text], ids=[doc_id])

        # יצירת רשומה במסד הנתונים
        bot_record = Bot(
            id=bot_id,
            owner_id=user_id,
            collection_name=bot_id,
            status="active",
            created_at=datetime.utcnow()
        )
        db.session.add(bot_record)
        db.session.commit()

        # איפוס היסטוריה ו-session relevant data
        session.pop("history", None)
        session.pop("uploaded_files_pending", None)
        session.pop("raw_text_summaries_pending", None)
        session.pop("bot_created", None)

        session["current_bot_id"] = bot_id

        flash("הבוט החדש נוצר בהצלחה! ניתן להתחיל בשיחה.")
        return redirect(url_for("chat.chat_interface", bot_id=bot_id))

    except Exception as e:
        flash(f"שגיאה ביצירת הבוט: {e}")
        return redirect(url_for("onboard_gpt.onboard_gpt"))