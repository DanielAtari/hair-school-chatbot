from openai import OpenAI
from chromadb import PersistentClient
import uuid

client = OpenAI(api_key=None)  # המפתח יוזן בקובץ הראשי ויעבור כפרמטר
chroma_client = PersistentClient(path="chroma_db/master")
collection = chroma_client.get_or_create_collection("master_assistant")

# רשימת שאלות עיקריות לאיסוף מידע עסקי
BUSINESS_QUESTIONS = [
    "מה שם העסק שלך?",
    "תוכל לתאר בקצרה את הפעילות של העסק?",
    "מה שעות הפתיחה והסגירה?",
    "מה טווח המחירים שאתה מציע?",
    "האם המחירים כוללים מע\"מ?",
    "מה דרכי יצירת הקשר ללקוחות? (טלפון, אימייל)",
    "האם יש קישורים חשובים כמו אתר אינטרנט או וואטסאפ?",
    "איזה סגנון דיבור תרצה שהבוט ישתמש? (קליל, מקצועי, חמים וכו')",
    "האם תרצה להעלות קובץ מידע או קישור לאתר להעמקת המידע?"
]

def handle_business_conversation(user_input, messages, collection, client):
    # בדיקת מה השאלה האחרונה שנשאלה (מתוך היסטוריה)
    asked_questions = [m["content"] for m in messages if m["role"] == "assistant"]
    # מייצרים רשימת שאלות שטרם נשאלו
    remaining_questions = [q for q in BUSINESS_QUESTIONS if q not in asked_questions]

    # אם נשאלו כבר כל השאלות, עושים סיכום ובודקים חוסרים
    if not remaining_questions:
        system_prompt = """
        אתה בוט עסקי שמסכם את המידע שנאסף מהלקוח.
        בדוק אם חסרים פרטים קריטיים כמו שעות פעילות, דרכי יצירת קשר או טווח מחירים.
        אם יש חוסרים, בקש מהם לעדכן.
        אם הכל מוכן, אשר שהבוט מוכן ליצירת הקישור.
        """
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model="gpt-4",
            messages=full_messages
        )
        return response.choices[0].message.content

    # אחרת, נשאל את השאלה הבאה מתוך הרשימה
    next_question = remaining_questions[0]

    system_prompt = f"""
    אתה בוט עסקי חכם ונעים.
    שאל את בעל העסק את השאלה הבאה בצורה אדיבה וממוקדת:
    {next_question}

    אם המשתמש ענה קודם ותיקן את עצמו, קבל זאת ברוח טובה.
    """

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-4",
        messages=full_messages
    )

    return response.choices[0].message.content