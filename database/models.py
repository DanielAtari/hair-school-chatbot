from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    system_prompt = db.Column(db.Text, nullable=True)  # פרומפט מותאם לעסק
    token_limit_per_month = db.Column(db.Integer, default=100000)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bots = db.relationship('Bot', back_populates='business', cascade="all, delete-orphan")
    usage_logs = db.relationship('TokenUsageLog', back_populates='business')
    messages = db.relationship('Message', back_populates='business', cascade="all, delete-orphan")

class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.String(36), primary_key=True)  # UUID של הבוט
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True)  # יכול להיות None לבוט אישי
    owner_user_id = db.Column(db.Integer, nullable=True)  # מזהה משתמש אם רלוונטי
    collection_name = db.Column(db.String(100), nullable=False)  # שם הקולקשן ב-Chroma
    status = db.Column(db.String(20), default="active")  # active, inactive וכו'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    business = db.relationship('Business', back_populates='bots')
    messages = db.relationship('Message', back_populates='bot', cascade="all, delete-orphan")

class TokenUsageLog(db.Model):
    __tablename__ = 'token_usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))
    month = db.Column(db.String(7), nullable=False)  # פורמט: '2025-07'
    total_tokens = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    business = db.relationship('Business', back_populates='usage_logs')

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True)
    bot_id = db.Column(db.String(36), db.ForeignKey('bots.id'), nullable=True)
    role = db.Column(db.String(10), nullable=False)  # "user" או "assistant"
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    business = db.relationship('Business', back_populates='messages')
    bot = db.relationship('Bot', back_populates='messages')