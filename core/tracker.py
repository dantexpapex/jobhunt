from models.database import db
from models.job import Job
from models.application import Application
from models.cv import CV
from config import Config
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


class JobTracker:
    def __init__(self):
        self.STATUS_NEW = "new"
        self.STATUS_EVALUATED = "evaluated"
        self.STATUS_APPLIED = "applied"
        self.STATUS_INTERVIEW = "interview"
        self.STATUS_REJECTED = "rejected"
        self.STATUS_OFFER = "offer"

    def add_job(self, job_data):
        existing = Job.query.filter_by(external_id=job_data.get("external_id")).first()
        if existing:
            logger.info(f"Job {job_data.get('external_id')} already exists")
            return existing

        job = Job(
            external_id=job_data.get("external_id"),
            title=job_data.get("title"),
            company=job_data.get("company"),
            location=job_data.get("location"),
            description=job_data.get("description"),
            url=job_data.get("url"),
            portal=job_data.get("portal"),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            salary_currency=job_data.get("salary_currency"),
            remote_type=job_data.get("remote_type"),
            experience_level=job_data.get("experience_level"),
            tech_stack=job_data.get("tech_stack"),
            company_size=job_data.get("company_size"),
            status=self.STATUS_NEW,
        )

        db.session.add(job)
        db.session.commit()
        logger.info(f"Added job: {job.title} at {job.company}")
        return job

    def update_job_status(self, job_id, status):
        job = Job.query.get(job_id)
        if job:
            job.status = status
            db.session.commit()
            logger.info(f"Updated job {job_id} status to {status}")
            return job
        return None

    def update_job_score(self, job_id, score, score_details=None):
        job = Job.query.get(job_id)
        if job:
            job.score = score
            job.score_details = score_details
            db.session.commit()
            return job
        return None

    def get_jobs_by_status(self, status):
        return Job.query.filter_by(status=status).all()

    def get_jobs_to_apply(self, min_score=70):
        return (
            Job.query.filter(
                Job.score >= min_score,
                Job.status.in_([self.STATUS_NEW, self.STATUS_EVALUATED]),
            )
            .order_by(Job.score.desc())
            .all()
        )

    def create_application(self, job_id, cv_id=None):
        existing = Application.query.filter_by(job_id=job_id).first()
        if existing:
            logger.info(f"Application for job {job_id} already exists")
            return existing

        application = Application(job_id=job_id, cv_id=cv_id, status="pending")

        db.session.add(application)

        job = Job.query.get(job_id)
        if job:
            job.status = self.STATUS_APPLIED

        db.session.commit()
        logger.info(f"Created application for job {job_id}")
        return application

    def update_application_status(self, application_id, status, notes=None):
        application = Application.query.get(application_id)
        if application:
            application.status = status
            if notes:
                application.notes = notes
            db.session.commit()
            logger.info(f"Updated application {application_id} status to {status}")
            return application
        return None

    def get_stats(self):
        total_jobs = Job.query.count()
        total_applications = Application.query.count()

        status_counts = (
            db.session.query(Job.status, func.count(Job.id)).group_by(Job.status).all()
        )

        applied_count = Application.query.filter_by(status="pending").count()
        interview_count = Application.query.filter_by(status="applied").count()
        interview_count = Application.query.filter_by(status="interview").count()

        return {
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "status_counts": dict(status_counts),
            "applied": applied_count,
            "interviews": interview_count,
        }

    def get_recent_jobs(self, limit=20):
        return Job.query.order_by(Job.created_at.desc()).limit(limit).all()

    def get_top_companies(self, limit=10):
        return (
            db.session.query(Job.company, func.count(Job.id).label("count"))
            .group_by(Job.company)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
            .all()
        )

    def mark_as_interview(self, job_id):
        return self.update_job_status(job_id, self.STATUS_INTERVIEW)

    def mark_as_rejected(self, job_id):
        return self.update_job_status(job_id, self.STATUS_REJECTED)

    def mark_as_offer(self, job_id):
        return self.update_job_status(job_id, self.STATUS_OFFER)


def add_cv(cv_data):
    cv = CV(
        name=cv_data.get("name"),
        file_path=cv_data.get("file_path"),
        base_cv=cv_data.get("base_cv", False),
        target_company=cv_data.get("target_company"),
        keywords=cv_data.get("keywords"),
        content=cv_data.get("content"),
    )

    db.session.add(cv)
    db.session.commit()
    return cv


def get_base_cv():
    return CV.query.filter_by(base_cv=True).first()


def get_cvs():
    return CV.query.all()
