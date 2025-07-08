from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from openai import OpenAI
from chromadb import PersistentClient
import os
import io
import uuid

import pdfplumber
import docx

onboard_gpt_bp = Blueprint("onboard_gpt", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = PersistentClient(path="chroma_db/master")
collection = chroma_client.get_or_create_collection("master_assistant")

MAX_TEXT_LENGTH = 5000  # מגבלה על אורך הטקסט הכולל שהועלה

def extract_text_pdf(file_stream):
    text = ""
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_docx(file_stream):
    doc = docx.Document(file_stream)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def extract_text_txt(file_stream):
    return file_stream.read().decode("utf-8").strip()

def extract_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    file_stream = io.BytesIO(file_storage.read())
    file_storage.seek(0)  # איפוס המצביע לקריאה חוזרת

    if filename.endswith(".pdf"):
        return extract_text_pdf(file_stream)
    elif filename.endswith(".docx"):
        return extract_text_docx(file_stream)
    elif filename.endswith(".txt"):
        return extract_text_txt(file_stream)
    else:
        return ""

@onboard_gpt_bp.route("/onboard-gpt", methods=["GET", "POST"])
def onboard_gpt():
    if "history" not in session:
        session["history"] = []
    if "uploaded_files_pending" not in session:
        session["uploaded_files_pending"] = []
    if "raw_text_summaries_pending" not in session:
        session["raw_text_summaries_pending"] = []
    if "bot_created" not in session:
        session["bot_created"] = False

    messages = session["history"]

    # אתחול שיחה ואיפוס
    if request.method == "POST":
        if "reset" in request.form:
            session.clear()
            flash("השיחה אותחלה. אפשר להתחיל מחדש.")
            return redirect(url_for("onboard_gpt.onboard_gpt"))

        if "remove_upload" in request.form:
            idx = int(request.form.get("remove_index", -1))
            total_pending = len(session["uploaded_files_pending"]) + len(session["raw_text_summaries_pending"])
            if 0 <= idx < total_pending:
                if idx < len(session["uploaded_files_pending"]):
                    removed = session["uploaded_files_pending"].pop(idx)
                else:
                    idx_adj = idx - len(session["uploaded_files_pending"])
                    removed = session["raw_text_summaries_pending"].pop(idx_adj)
                flash("הפריט הוסר בהצלחה.")
            else:
                flash("פריט לא נמצא להסרה.")
            return redirect(url_for("onboard_gpt.onboard_gpt"))

        if "confirm_uploads" in request.form:
            # כאן נטען את כל המידע הסופי ל-Chroma
            try:
                for text in session["uploaded_files_pending"]:
                    doc_id = str(uuid.uuid4())
                    collection.add(documents=[text], ids=[doc_id])
                for summary in session["raw_text_summaries_pending"]:
                    doc_id = str(uuid.uuid4())
                    collection.add(documents=[summary], ids=[doc_id])
                # ניקוי הרשימות הזמניות לאחר טעינה
                session["uploaded_files_pending"] = []
                session["raw_text_summaries_pending"] = []
                session["bot_created"] = True  # מציין שהבוט מוכן ליצירה
                flash("המידע אושר ונטען למאגר הידע. אפשר להמשיך ליצירת הבוט.")
            except Exception as e:
                flash(f"שגיאה בטעינת המידע: {e}")
            return redirect(url_for("onboard_gpt.onboard_gpt"))

    # אם הבוט כבר נוצר - מעבירים ליצירת בוט (הנתיב נניח /create-bot)
    if session.get("bot_created", False):
        return redirect(url_for("bot_creation.create_bot"))

    if request.method == "POST":
        # טיפול בהעלאת קבצים חדשים
        uploaded_files = request.files.getlist("file")
        if uploaded_files:
            for file in uploaded_files:
                if file and file.filename != "":
                    text = extract_text_from_file(file)
                    if not text:
                        flash(f"הקובץ '{file.filename}' לא נתמך או ריק.")
                        return redirect(url_for("onboard_gpt.onboard_gpt"))

                    total_length = sum(len(t) for t in session["uploaded_files_pending"] + session["raw_text_summaries_pending"]) + len(text)
                    if total_length > MAX_TEXT_LENGTH:
                        flash(f"הקובץ '{file.filename}' גדול מדי. המגבלה הכוללת היא {MAX_TEXT_LENGTH} תווים.")
                        return redirect(url_for("onboard_gpt.onboard_gpt"))

                    session["uploaded_files_pending"].append(text)
                    flash(f"הקובץ '{file.filename}' הועלה בהצלחה, אך עדיין לא נטען למאגר הידע.")

            return redirect(url_for("onboard_gpt.onboard_gpt"))

        # טיפול בהודעת טקסט רגילה - raw text חופשי
        user_input = request.form.get("message", "").strip()
        if user_input:
            messages.append({"role": "user", "content": user_input})
            # שליחת טקסט חופשי לסיכום לפני הוספה ל-chroma
            system_prompt = """
            סכם את הטקסט הבא בקצרה, כך שיהיה נוח לשלב במאגר הידע:
            """
            full_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=full_messages
                )
                summary = response.choices[0].message.content.strip()
                session["raw_text_summaries_pending"].append(summary)
                flash("הטקסט שלך סוכם והתווסף למידע הממתין לאישור.")
            except Exception as e:
                flash(f"שגיאה בסיכום הטקסט: {e}")

            session["history"] = messages
            return redirect(url_for("onboard_gpt.onboard_gpt"))

    return render_template(
        "onboard_gpt.html",
        history=messages,
        uploaded_files_pending=session.get("uploaded_files_pending", []),
        raw_text_summaries_pending=session.get("raw_text_summaries_pending", [])
    )