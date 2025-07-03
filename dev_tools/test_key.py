import os
from dotenv import load_dotenv
from openai import OpenAI

# טוען את המפתח מקובץ .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("Loaded key:", api_key)

# בדיקת חיבור ל־OpenAI
try:
    client = OpenAI(api_key=api_key)
    response = client.models.list()
    print("✅ החיבור ל־OpenAI הצליח! אלה המודלים הזמינים:")
    for model in response.data[:5]:
        print("-", model.id)
except Exception as e:
    print("❌ שגיאה בחיבור ל־OpenAI:")
    print(e)
