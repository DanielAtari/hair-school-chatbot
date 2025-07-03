import chromadb
from chromadb import PersistentClient
import json

# יצירת חיבור למסד המקומי
client = PersistentClient(path="./chroma_db")

# יצירת קולקשן (או קיים כבר)
collection = client.get_or_create_collection("hair_school")

# קריאת הקובץ JSON
with open("hair_school_chroma_split_docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# הכנסת הטקסטים למסד הנתונים (רק טקסטים מתוך כל אובייקט)
collection.add(
    documents=[doc["text"] for doc in data],
    ids=[f"doc_{i}" for i in range(len(data))]
)

print("✅ הנתונים הוזנו בהצלחה ל-Chroma.")
