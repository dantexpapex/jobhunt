from models.database import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    portal = db.Column(db.String(50))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10))
    remote_type = db.Column(db.String(50))
    experience_level = db.Column(db.String(50))
    tech_stack = db.Column(db.Text)
    company_size = db.Column(db.String(50))
    status = db.Column(db.String(50), default="new")
    score = db.Column(db.Float)
    score_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications = db.relationship("Application", backref="job", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "url": self.url,
            "portal": self.portal,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "remote_type": self.remote_type,
            "experience_level": self.experience_level,
            "tech_stack": self.tech_stack,
            "company_size": self.company_size,
            "status": self.status,
            "score": self.score,
            "score_details": self.score_details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
