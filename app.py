# app.py

from flask import Flask, request, Response, render_template, redirect, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import chromadb
from chromadb import PersistentClient
from database.config import Config
from database.models import db, Business, TokenUsageLog
from datetime import datetime
from pathlib import Path

# טעינת משתני סביבה מקובץ .env גם אם מריצים ממקום אחר
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
print("Loaded key:", os.getenv('OPENAI_API_KEY'))
print("Database URI:", os.getenv('DATABASE_URL'))

# יצירת Flask app
app = Flask(__name__)

# הגדרות SQLAlchemy
app.config.from_object(Config)
db.init_app(app)

# יצירת טבלאות (למי שלא יכול להשתמש ב-@before_first_request)
with app.app_context():
    db.create_all()

# חיבור ל-OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# חיבור למסד הנתונים של Chroma
chroma_client = PersistentClient(path="/tmp/chroma_db")
collection = chroma_client.get_or_create_collection("hair_school")

SYSTEM_PROMPT_FILE = "system_prompt.txt"

# פונקציית טעינת system prompt
def load_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_FILE):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "אתה עוזר ללקוח במענה לשאלות על בית ספר לעיצוב שיער. התנהג בצורה אדיבה, חייכנית, מזמינה, לא רצינית מידי ולא רובוטית."

# פונקציית חיפוש לפי שאלה
def retrieve_context_from_chroma(query, k=3):
    results = collection.query(query_texts=[query], n_results=k)
    return "\n".join(results["documents"][0]) if results["documents"] else ""

# פונקציית הצ'אטבוט
def chatbot(question):
    try:
        context = retrieve_context_from_chroma(question)
        system_prompt = load_system_prompt()
        full_system_prompt = f"{system_prompt}\n\nהשתמש בטקסט הבא כדי לענות לשאלות בצורה מדויקת ומועילה:\n\n{context}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"שגיאה: {str(e)}"

@app.route("/")
def home():
    return "ברוך הבא לצ׳אטבוט של Atara! האפליקציה פעילה. 🎯"

@app.route("/edit", methods=["GET"])
def edit_text():
    try:
        with open("hair_school_raw_text.txt", "r", encoding="utf-8") as f:
            current_text = f.read()
    except FileNotFoundError:
        current_text = ""
    return render_template("editor.html", current_text=current_text)

@app.route("/save", methods=["POST"])
def save_text():
    new_text = request.form.get("text", "")

    with open("hair_school_raw_text.txt", "w", encoding="utf-8") as f:
        f.write(new_text)

    paragraphs = [p.strip() for p in new_text.split("\n\n") if p.strip()]
    data = [{"text": p} for p in paragraphs]

    with open("hair_school_chroma_split_docs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    collection.delete(ids=collection.get()["ids"])

    collection.add(
        documents=[doc["text"] for doc in data],
        ids=[f"doc_{i}" for i in range(len(data))]
    )

    return redirect("/edit")

@app.route("/edit_system_prompt", methods=["GET"])
def edit_system_prompt():
    current_prompt = load_system_prompt()
    return render_template("system_prompt_editor.html", current_prompt=current_prompt)

@app.route("/save_system_prompt", methods=["POST"])
def save_system_prompt_route():
    new_prompt = request.form.get("system_prompt", "")
    with open(SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(new_prompt)
    return redirect("/edit_system_prompt")

# API לעדכון טוקנים
@app.route("/update_tokens", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
