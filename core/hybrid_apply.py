from models.database import db
from models.job import Job
from models.application import Application
from models.cv import CV
from config import Config
import logging

logger = logging.getLogger(__name__)


class HybridAutoApplier:
    MODE_MANUAL_ONLY = "manual"
    MODE_AUTO_TRY_FIRST = "auto_try"
    MODE_HYBRID = "hybrid"

    def __init__(self, mode=MODE_HYBRID):
        self.mode = mode
        self.auto_apply_enabled = Config.AUTO_APPLY_ENABLED

    def create_application(self, job_id, cv_id=None, generate_docs=True):
        existing = Application.query.filter_by(job_id=job_id).first()
        if existing:
            logger.info(f"Application for job {job_id} already exists")
            return existing

        job = Job.query.get(job_id)
        if not job:
            return None

        if cv_id is None:
            from core.cv_manager import auto_select_cv

            cv_obj = auto_select_cv(job_id)
            cv_id = cv_obj.id if cv_obj else None

        application = Application(
            job_id=job_id, cv_id=cv_id, status="pending_review", needs_review=True
        )

        if generate_docs:
            from core.cv_manager import CVManager
            from core.cv_adapter import adapt_cv_for_job, extract_personal_info_from_cv
            from core.cover_letter import generate_cover_letter

            cv_manager = CVManager()
            recommended_cv = cv_manager.get_recommended_cv(
                job.title, remote=(job.remote_type == "remote")
            )

            if recommended_cv:
                job_data = {
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                }

                adapted_cv_path = adapt_cv_for_job(recommended_cv["path"], job_data)
                application.cv_path = adapted_cv_path

                cv_content = cv_manager.extract_content_from_docx(
                    recommended_cv["path"]
                )
                personal_info = extract_personal_info_from_cv(cv_content)
                cover_letter = generate_cover_letter(job_data, personal_info)

                if cover_letter:
                    from core.cover_letter import save_cover_letter

                    path = save_cover_letter(cover_letter, job.company, job.title)
                    application.cover_letter_path = path

        db.session.add(application)
        db.session.commit()

        job.status = "pending_review"
        db.session.commit()

        logger.info(f"Created application {application.id} for job {job_id}")
        return application

    def approve_application(self, application_id):
        application = Application.query.get(application_id)
        if not application:
            return None

        application.status = "ready_to_apply"
        application.needs_review = False
        application.reviewed_at = db.func.now()

        job = Job.query.get(application.job_id)
        if job:
            job.status = "approved"

        db.session.commit()
        logger.info(f"Application {application_id} approved")
        return application

    def reject_application(self, application_id, reason=None):
        application = Application.query.get(application_id)
        if not application:
            return None

        application.status = "rejected"
        application.needs_review = False
        application.notes = reason
        application.reviewed_at = db.func.now()

        job = Job.query.get(application.job_id)
        if job:
            job.status = "rejected"

        db.session.commit()
        logger.info(f"Application {application_id} rejected: {reason}")
        return application

    def apply_to_approved(self):
        from core.auto_applier import apply_with_delay

        applications = (
            Application.query.filter_by(status="ready_to_apply")
            .limit(Config.MAX_APPLICATIONS_PER_DAY)
            .all()
        )

        results = []
        for app in applications:
            job = Job.query.get(app.job_id)
            if not job:
                continue

            if self.mode == self.MODE_MANUAL_ONLY:
                results.append(
                    {
                        "application_id": app.id,
                        "status": "manual_action_needed",
                        "job_url": job.url,
                    }
                )
                continue

            try:
                from core.auto_applier import apply_with_delay

                success = apply_with_delay(job.url, app.cv_path, delay_seconds=5)

                app.auto_apply_attempted = True
                app.auto_apply_success = success
                app.applied_at = db.func.now()

                if success:
                    app.status = "applied"
                else:
                    app.status = "auto_failed"

                db.session.commit()

                results.append(
                    {"application_id": app.id, "success": success, "job": job.title}
                )

            except Exception as e:
                logger.error(f"Auto apply failed for {app.id}: {e}")
                app.status = "auto_failed"
                db.session.commit()

                results.append(
                    {"application_id": app.id, "success": False, "error": str(e)}
                )

        return results

    def get_pending_review(self, limit=20):
        return (
            Application.query.filter_by(needs_review=True, status="pending_review")
            .order_by(Application.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_ready_to_apply(self):
        return Application.query.filter_by(status="ready_to_apply").all()

    def get_applied_today(self):
        from datetime import datetime, timedelta

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return Application.query.filter(Application.applied_at >= today).all()


def queue_application(job_id):
    applier = HybridAutoApplier()
    return applier.create_application(job_id)


def approve_application(application_id):
    applier = HybridAutoApplier()
    return applier.approve_application(application_id)


def reject_application(application_id, reason=None):
    applier = HybridAutoApplier()
    return applier.reject_application(application_id, reason)


def run_auto_apply():
    applier = HybridAutoApplier(mode=HybridAutoApplier.MODE_HYBRID)
    return applier.apply_to_approved()


def get_dashboard_stats():
    pending = Application.query.filter_by(status="pending_review").count()
    ready = Application.query.filter_by(status="ready_to_apply").count()
    applied = Application.query.filter_by(status="applied").count()
    auto_failed = Application.query.filter_by(status="auto_failed").count()

    return {
        "pending_review": pending,
        "ready_to_apply": ready,
        "applied": applied,
        "auto_failed": auto_failed,
    }
