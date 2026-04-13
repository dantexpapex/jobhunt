from flask import Blueprint, render_template, request, redirect, url_for
from core.tracker import JobTracker

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    tracker = JobTracker()
    stats = tracker.get_stats()
    return render_template("dashboard.html", stats=stats)


@bp.route("/jobs")
def jobs():
    status = request.args.get("status")
    tracker = JobTracker()
    if status:
        job_list = tracker.get_jobs_by_status(status)
    else:
        job_list = tracker.get_recent_jobs(100)
    return render_template("jobs.html", jobs=job_list, status=status)


@bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    from models.job import Job

    job = Job.query.get(job_id)
    return render_template("job_detail.html", job=job)


@bp.route("/apply/<int:job_id>", methods=["POST"])
def apply_to_job(job_id):
    tracker = JobTracker()
    tracker.create_application(job_id)
    return redirect(url_for("web.jobs"))


@bp.route("/settings")
def settings():
    return render_template("settings.html")


@bp.route("/stats")
def stats():
    tracker = JobTracker()
    stats = tracker.get_stats()
    top_companies = tracker.get_top_companies(10)
    return render_template("stats.html", stats=stats, top_companies=top_companies)


@bp.route("/interview")
def interview():
    return render_template("interview.html")


@bp.route("/applications")
def applications():
    from core.hybrid_apply import get_dashboard_stats, HybridAutoApplier

    applier = HybridAutoApplier()
    stats = get_dashboard_stats()
    pending = applier.get_pending_review(20)

    return render_template(
        "applications.html", stats=stats, pending_applications=pending
    )
