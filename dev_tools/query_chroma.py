import chromadb
from chromadb import PersistentClient

# התחברות למסד הנתונים המקומי
client = PersistentClient(path="./chroma_db")

# שליפת הקולקשן
collection = client.get_collection("hair_school")

# ניסוח השאילתה
query = "אני גונח לזווית, אפשר להחסיר שיעורים?"

# ביצוע השאילתה וקבלת תוצאות
results = collection.query(
    query_texts=[query],
    n_results=2
)

# הדפסת תוצאות
for i, doc in enumerate(results["documents"][0]):
    print(f"\n—– תוצאה {i+1} —–")
    print(doc)
