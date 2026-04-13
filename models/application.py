from models.database import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    cv_id = db.Column(db.Integer, db.ForeignKey("cvs.id"))
    status = db.Column(db.String(50), default="pending_review")
    applied_at = db.Column(db.DateTime)
    response_received = db.Column(db.Boolean, default=False)
    response_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    cover_letter_path = db.Column(db.String(500))
    cv_path = db.Column(db.String(500))
    needs_review = db.Column(db.Boolean, default=True)
    reviewed_by = db.Column(db.String(50))
    reviewed_at = db.Column(db.DateTime)
    auto_apply_attempted = db.Column(db.Boolean, default=False)
    auto_apply_success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "cv_id": self.cv_id,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "response_received": self.response_received,
            "notes": self.notes,
            "needs_review": self.needs_review,
            "auto_apply_attempted": self.auto_apply_attempted,
            "auto_apply_success": self.auto_apply_success,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


APPLICATION_STATUS = {
    "PENDING_REVIEW": "pending_review",
    "APPROVED": "approved",
    "REJECTED": "rejected",
    "READY_TO_APPLY": "ready_to_apply",
    "APPLIED": "applied",
    "AUTO_FAILED": "auto_failed",
    "INTERVIEW": "interview",
    "REJECTED_BY_EMPLOYER": "rejected",
    "OFFER": "offer",
}
