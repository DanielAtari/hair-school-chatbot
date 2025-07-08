from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from openai import OpenAI
from chromadb import PersistentClient
import os
import io

import pdfplumber
import docx
import fitz  # PyMuPDF

onboard_gpt_bp = Blueprint("onboard_gpt", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = PersistentClient(path="chroma_db/master")
collection = chroma_client.get_or_create_collection("master_assistant")

# פונקציות עזר לקריאת טקסט מקבצים שונים
def extract_text_pdf(file_stream):
    text = ""
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_docx(file_stream):
    doc = docx.Document(file_stream)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def extract_text_txt(file_stream):
    return file_stream.read().decode('utf-8').strip()

@onboard_gpt_bp.route("/onboard-gpt", methods=["GET", "POST"])
def onboard_gpt():
    if "history" not in session:
        session["history"] = []

    messages = session["history"]
    uploaded_text = None

    if request.method == "POST":
        # טיפול בהעלאת קובץ
        file = request.files.get("file")
        if file and file.filename != "":
            filename = file.filename.lower()
            file_stream = io.BytesIO(file.read())
            if filename.endswith(".pdf"):
                uploaded_text = extract_text_pdf(file_stream)
            elif filename.endswith(".docx"):
                uploaded_text = extract_text_docx(file_stream)
            elif filename.endswith(".txt"):
                uploaded_text = extract_text_txt(file_stream)
            else:
                flash("סוג הקובץ לא נתמך. אנא העלה PDF, DOCX או TXT.")
                return redirect(url_for("onboard_gpt.onboard_gpt"))

            # הוסף טקסט שהועלה כהודעה סיסטם מיוחדת (אפשר גם כמשתמש)
            messages.append({"role": "system", "content": f"הלקוח העלה את הטקסט הבא:\n{uploaded_text}"})

        # טיפול בהודעת טקסט רגילה
        user_input = request.form.get("message")
        if user_input:
            messages.append({"role": "user", "content": user_input})

        # שליפת הקשר מ-Chroma
        query_text = user_input if user_input else uploaded_text if uploaded_text else ""
        chroma_results = collection.query(query_texts=[query_text], n_results=2)
        context = "\n".join(chroma_results["documents"][0]) if chroma_results["documents"] else ""

        # פרומט ראשי
        system_prompt = """
אתה הבוט הראשי של Atara להקמת צ'אט לעסקים.

מטרתך לעזור לבעל העסק להקים בוט חכם, מדויק ונעים.

שאל שאלה אחת בכל פעם, בטון אדיב וממוקד.

אם הלקוח מתקן את עצמו, קבל זאת ברוח טובה.

אם משהו לא ברור או חסר, בקש הבהרה בעדינות.

חשוב להסביר למה כל שאלה נשאלת, כדי להקל על הלקוח.
"""

        full_system_prompt = system_prompt + "\nהקשר נוסף מהידע שיש לך:\n" + context

        # בניית ההיסטוריה עם הפרומט והודעות
        full_messages = [{"role": "system", "content": full_system_prompt}] + messages

        # קריאה ל־OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=full_messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        session["history"] = messages

    return render_template("onboard_gpt.html", history=messages)

import os
from chromadb import PersistentClient
import json

print("🚀 מתחילים את תהליך ההטענה...")

# יצירת חיבור ל-Chroma
client = PersistentClient(path="chroma_db/master")
collection = client.get_or_create_collection("master_assistant")

# בדיקה שהקולקשן נוצר
print(f"✅ קולקשן '{collection.name}' מוכן לשימוש.")

# נתיב הקובץ JSON
json_path = "scripts/business_categories_questions.json"
print(f"📂 טוען קובץ JSON מ: {os.path.abspath(json_path)}")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"✅ טענו JSON עם {len(data)} קטגוריות.")

# טעינת הקטגוריות ל-Chroma
for i, (category, content) in enumerate(data.items()):
    category_text = f"קטגוריה: {category}\n"
    category_text += "סוגי עסקים:\n" + "\n".join(f"- {t}" for t in content["types"]) + "\n"
    category_text += "שאלות שכדאי לשאול:\n" + "\n".join(f"- {q}" for q in content["questions"])
    collection.add(
        documents=[category_text],
        ids=[f"business_category_{i}"]
    )
    print(f"  + קטגוריה '{category}' הוזנה בהצלחה.")

print("🎉 כל הקטגוריות נטענו ל-Chroma בהצלחה!")
