import logging
import chromadb
from chromadb import PersistentClient
import tiktoken
import os

# קונפיגורציית הלוגינג הבסיסית
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# יצירת נתיב קבוע ל-ChromaDB בתוך תיקיית הפרויקט
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
client = PersistentClient(path=CHROMA_PATH)

def get_chroma_collection(business_id):
    collection_name = f"biz_{business_id}"
    return client.get_or_create_collection(name=collection_name)

def retrieve_context_from_chroma(business_id, query, k=3):
    collection = get_chroma_collection(business_id)
    results = collection.query(query_texts=[query], n_results=k)
    return "\n".join(results["documents"][0]) if results["documents"] else ""

def split_text(text, max_tokens=200):
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split("\n")
    chunks, current_chunk = [], []
    current_len = 0

    for line in words:
        tokens = len(enc.encode(line))
        if current_len + tokens > max_tokens:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_len = tokens
        else:
            current_chunk.append(line)
            current_len += tokens

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

def load_business_knowledge(business_id, raw_text):
    if not raw_text.strip():
        logging.warning("⚠️ אזהרה: אין טקסט להעלות")
        return 0  # אין תוכן להוסיף

    collection = get_chroma_collection(business_id)
    logging.info(f"🚀 מתחילים טעינת ידע לעסק {business_id}...")

    try:
        results = collection.get()
        all_ids = results.get("ids", [])
        if all_ids:
            collection.delete(ids=all_ids)
            logging.info(f"🗑️ נמחקו {len(all_ids)} פריטים ישנים מהקולקשן")
        else:
            logging.info("ℹ️ אין פריטים ישנים למחיקה")
    except Exception as e:
        logging.error(f"⚠️ שגיאה במחיקת תוכן ישן: {e}")

    chunks = split_text(raw_text)
    documents = [chunk for chunk in chunks if chunk.strip()]
    ids = [f"{business_id}_{i}" for i in range(len(documents))]

    try:
        collection.add(documents=documents, ids=ids)
        logging.info(f"✅ נטענו {len(documents)} קטעים חדשים ל־Chroma")
    except Exception as e:
        logging.error(f"⚠️ שגיאה בהוספת תוכן חדש: {e}")
        return 0

    return len(documents)
