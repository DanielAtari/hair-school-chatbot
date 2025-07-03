# GPT SaaS Platform for Businesses

This is a SaaS solution that allows businesses to create a personalized GPT-powered chatbot, backed by a vector database (ChromaDB). Each business can upload their own content, which the chatbot uses to respond accurately to customer questions. The platform includes user-friendly conversation management, token usage tracking, and support for real-time human takeover.

## 🚀 Features

- 💬 GPT-powered chatbot trained on your business data.
- 📁 Upload your own content (text → vector embeddings via OpenAI API).
- 🧠 ChromaDB integration for semantic search and retrieval.
- 📊 Track usage per business (token-based billing, per conversation).
- 📂 Automatic business onboarding (via unique customer link).
- 🧑‍💼 Real-time owner participation in bot conversations (human handoff).
- 💬 Conversation logging and history management.
- 🔒 Environment variable handling (.env support).
- 🌐 Heroku-ready deployment (Procfile & runtime.txt included).
- 🧑‍💼 Future: Admin dashboard + Web frontend for business owners.

## 📁 Project Structure

```
project/
├── chroma_db/
├── database/
├── instance/
├── templates/
├── app.py
├── load_to_chroma.py
├── query_chroma.py
├── test_key.py
├── hair_school_raw_text.txt
├── system_prompt.txt
├── .env
├── .gitignore
├── requirements.txt
├── runtime.txt
├── Procfile
```

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/your-saas-gpt.git
cd your-saas-gpt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set your `.env` file:
```env
OPENAI_API_KEY=sk-...
```

## 📡 Running the App

```bash
python app.py
```

## 🔄 Uploading Business Data

Use `load_to_chroma.py` to embed business documents into the Chroma vector DB.

## 💬 Querying Data

Use `query_chroma.py` to test GPT responses using semantic similarity.

## 👥 Real-Time Owner Participation

The platform supports human handoff for real-time business owner chat override.

## 📈 Token Usage Tracking

Messages are logged with token count per business and conversation.

## 🔜 Upcoming Features

- Web UI for business onboarding and dashboard
- Stripe integration for token-based billing
- Business content editing
- Owner/staff roles

## 📧 Contact

For support or collaboration, contact: `your-email@example.com`

---

# פלטפורמת GPT לעסקים (SaaS)

זהו פתרון SaaS שמאפשר לעסקים ליצור צ'אטבוט מותאם אישית, מבוסס GPT, הנשען על מסד נתוני וקטורים (ChromaDB). כל עסק מעלה תוכן משלו, והבוט משתמש בו כדי להשיב ללקוחות באופן מדויק. המערכת כוללת ניהול שיחות, מעקב טוקנים, ותמיכה בהצטרפות של מנהל לשיחה.

## 🚀 תכונות מרכזיות

- 💬 צ'אטבוט מבוסס GPT על בסיס תוכן העסק.
- 📁 טעינת טקסט והמרתו ל־embeddings דרך OpenAI.
- 🧠 אינטגרציה עם ChromaDB לחיפוש סמנטי.
- 📊 מעקב שימוש בטוקנים לפי עסק.
- 📂 חיבור לקוחות לעסק דרך קישור ייחודי.
- 👥 אפשרות למנהל להצטרף לשיחה במקום הבוט.
- 💬 שמירת שיחות וניהול היסטוריה.
- 🔒 שימוש בקובץ .env לניהול מפתחות.
- 🌐 מוכן להרצה ב-Heroku.
- 🧑‍💼 בעתיד: דאשבורד לבעל העסק + פרונטאנד.

## 📁 מבנה הפרויקט

```
project/
├── chroma_db/
├── database/
├── instance/
├── templates/
├── app.py
├── load_to_chroma.py
├── query_chroma.py
├── test_key.py
├── hair_school_raw_text.txt
├── system_prompt.txt
├── .env
├── .gitignore
├── requirements.txt
├── runtime.txt
├── Procfile
```

## 🛠️ התקנה

```bash
git clone https://github.com/yourusername/your-saas-gpt.git
cd your-saas-gpt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

קובץ .env:
```env
OPENAI_API_KEY=sk-...
```

## 📡 הרצת האפליקציה

```bash
python app.py
```

## 🔄 טעינת תוכן עסק

השתמש ב־`load_to_chroma.py` כדי להזין טקסטים לתוך Chroma.

## 💬 שאילתות למידע

השתמש ב־`query_chroma.py` כדי לבדוק תגובות מבוססות ידע.

## 👥 הצטרפות מנהל לשיחה

המערכת תומכת בהצטרפות בזמן אמת של בעל העסק כדי להשיב ללקוח במקום הבוט.

## 📈 מעקב אחר שימוש

כל שיחה מתועדת עם כמות הטוקנים, לצורך חיוב ובקרה.

## 🔜 בקרוב

- ממשק אינטרנטי לניהול עסק
- חיוב לפי שימוש ב־Stripe
- אפשרות עריכת תוכן
- תפקידים שונים לצוות ובעלים

## 📧 יצירת קשר

לשאלות או שיתופי פעולה: `your-email@example.com`