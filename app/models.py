import uuid
from datetime import datetime
from .db import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=True)
    question = db.Column(db.String, nullable=False)
    allow_text = db.Column(db.Boolean, default=False)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"))
    text = db.Column(db.String, nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.UUID, nullable=False)
    option_id = db.Column(db.Integer, nullable=True)
    text_answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("poll_id", "user_id"),
    )
