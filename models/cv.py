from models.database import db
from datetime import datetime


class CV(db.Model):
    __tablename__ = "cvs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    base_cv = db.Column(db.Boolean, default=False)
    target_company = db.Column(db.String(255))
    keywords = db.Column(db.Text)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications = db.relationship("Application", backref="cv", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "base_cv": self.base_cv,
            "target_company": self.target_company,
            "keywords": self.keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
