from database.models import db, Business, Message
from services.chroma_service import retrieve_context_from_chroma
from openai import OpenAI
from datetime import datetime
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chatbot(business_id, question):
    try:
        # שליפת הקשר סמנטי
        context = retrieve_context_from_chroma(business_id, question)

        # שליפת פרטי העסק
        business = db.session.query(Business).filter_by(id=business_id).first()
        system_prompt = business.system_prompt or "You are a helpful assistant."
        full_system_prompt = f"{system_prompt}\n\nUse the following context to assist the user:\n\n{context}"

        # שליפת ההיסטוריה (10 הודעות אחרונות, מסודרות מהעתיק לחדש)
        history = (
            db.session.query(Message)
            .filter_by(business_id=business_id)
            .order_by(Message.timestamp.desc())
            .limit(10)
            .all()
        )[::-1]  # היפוך לרצף כרונולוגי

        # בניית מערך ההודעות
        messages = [{"role": "system", "content": full_system_prompt}]
        for msg in history:
            role = msg.role
            if role == "bot":
                role = "assistant"
            elif role not in ["user", "assistant", "system"]:
                continue
            messages.append({"role": role, "content": msg.content})

        # הוספת השאלה הנוכחית
        messages.append({"role": "user", "content": question})

        # שליחה ל־GPT
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print("\u26a0\ufe0f OpenAI API Error:", e)
            return "שגיאה בשירות השיחה. אנא נסה שוב מאוחר יותר."

        return answer

    except Exception as e:
        print("\u26a0\ufe0f Unexpected Error:", e)
        return f"שגיאה: {str(e)}"