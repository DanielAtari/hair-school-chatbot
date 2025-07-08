from openai import OpenAI
from chromadb import PersistentClient
import uuid
import io

# לטעון את המפתחות ב־app הראשי ולהעביר לפרמטרים במידת הצורך
client = OpenAI(api_key=None)
chroma_client = PersistentClient(path="chroma_db/master")
collection = chroma_client.get_or_create_collection("master_assistant")

# רשימת שאלות ופקודות נפוצות למסלול האישי
PERSONAL_START_PROMPT = """
אתה בוט אישי, קליל והיתולי בשם 'נסיך עצמאי'.  
אתה שואל את המשתמש איך הוא רוצה שהאופי שלך יהיה (קליל, הומוריסטי, רציני וכו').  
אתה מסייע לארגן מידע אישי: מתכונים, שירים, סיפורים, רשימות ועוד.  
הייתה קשוב למשתמש, התייחס לתיקונים שלו וחזור עליו בנעימות.  
אם המשתמש מעלה קבצים, תעזור לו לארגן את התוכן.
"""

def extract_text_from_file(file_stream, filename):
    # פונקציית עזר לפענוח קבצים לפי סוג (אפשר להרחיב)
    import pdfplumber
    import docx

    filename = filename.lower()
    if filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    elif filename.endswith(".docx"):
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    elif filename.endswith(".txt"):
        return file_stream.read().decode("utf-8").strip()
    else:
        return ""

def handle_personal_conversation(user_input, messages, collection, client, uploaded_files=None):
    # טיפול בקבצים שהועלו
    if uploaded_files:
        for file in uploaded_files:
            file_stream = io.BytesIO(file.read())
            text = extract_text_from_file(file_stream, file.filename)
            if text:
                # מוסיפים למאגר הידע (Chroma)
                doc_id = str(uuid.uuid4())
                collection.add(documents=[text], ids=[doc_id])
        reply = "העליתי וארגנתי את התכנים ששלחת. איך תרצה להמשיך?"
        messages.append({"role": "assistant", "content": reply})
        return reply

    # אם אין קבצים, ממשיכים בשיחה עם GPT
    system_prompt = PERSONAL_START_PROMPT
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-4",
        messages=full_messages
    )
    return response.choices[0].message.content