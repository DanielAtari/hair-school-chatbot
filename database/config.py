import os
from dotenv import load_dotenv
from pathlib import Path

# טוען את .env כאן - בזמן ההגדרה, לא בקובץ הראשי
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
