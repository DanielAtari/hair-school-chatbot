
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    token_limit_per_month = db.Column(db.Integer, default=100000)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    usage_logs = db.relationship('TokenUsageLog', back_populates='business')


class TokenUsageLog(db.Model):
    __tablename__ = 'token_usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))
    month = db.Column(db.String(7), nullable=False)  # e.g., '2025-07'
    total_tokens = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    business = db.relationship('Business', back_populates='usage_logs')
