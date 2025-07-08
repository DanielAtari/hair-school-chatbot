from flask import Flask
from dotenv import load_dotenv
from pathlib import Path
import os
from flask_migrate import Migrate
from flask_session import Session
from routes.onboard_gpt import onboard_gpt_bp

# הגדרות וקונפיגורציה
from database.config import Config
from database.models import db

# טעינת משתני סביבה מהקובץ .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# יצירת אפליקציית Flask והגדרות
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY")

# חיבור למסד הנתונים והפעלת מיגרציות
db.init_app(app)
migrate = Migrate(app, db)

app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# ייבוא והרשמה של ה־Blueprints
from routes.chat import chat_bp
from routes.tokens import tokens_bp
from routes.upload import upload_bp
from routes.admin import admin_bp
from routes.onboard_gpt import onboard_gpt_bp
from routes.bot_creation import bot_creation_bp


app.register_blueprint(chat_bp)
app.register_blueprint(tokens_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(onboard_gpt_bp)
app.register_blueprint(bot_creation_bp)

# דף בית לבדיקה שהאפליקציה פועלת
@app.route("/", methods=["GET"])
def home():
    return "האפליקציה פועלת! ברוך הבא ל־Atara: בוט לשירות לקוחות חכם"

if __name__ == "__main__":
    app.run(debug=True)