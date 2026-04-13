from flask import Blueprint, jsonify, request
from models.database import db
from models.job import Job
from models.application import Application
from models.cv import CV
from core.scraper import search_jobs, search_remote_jobs, format_job_data
from core.analyzer import analyze_job
from core.tracker import JobTracker
from core.cv_generator import CVGenerator
from core.cover_letter import generate_cover_letter_for_job, save_cover_letter
from core.interview_prep import (
    generate_interviewPrep_for_job,
    practice_interview,
    get_salary_insights,
)
from core.hybrid_apply import (
    queue_application,
    approve_application,
    reject_application,
    run_auto_apply,
    get_dashboard_stats,
)
from core.ai_engine import (
    analyze_job_with_ai,
    extract_ats_keywords,
    compare_with_profile,
    generate_cover_letter_with_ai,
    generate_interview_questions,
    chat_with_ai,
)
from core.sheets_tracker import (
    add_to_sheets,
    update_sheets_status,
    get_sheets_stats,
    sync_sheets,
    get_all_from_sheets,
)
from core.local_tracker import (
    add_application,
    update_tracker_status,
    get_tracker_stats,
    sync_from_db,
    get_all_tracker,
)
from core.advanced_features import (
    get_company_ranking,
    rank_companies,
    predict_success,
)
from core.interview_bot import (
    generate_interview_response,
    generate_follow_up_email,
    generate_interview_cheatsheet,
)
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@bp.route("/jobs", methods=["GET"])
def get_jobs():
    status = request.args.get("status")
    limit = request.args.get("limit", 50, type=int)

    query = Job.query
    if status:
        query = query.filter_by(status=status)

    jobs = query.order_by(Job.created_at.desc()).limit(limit).all()
    return jsonify([job.to_dict() for job in jobs])


@bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())


@bp.route("/jobs/<int:job_id>/analyze", methods=["POST"])
def analyze_job_endpoint(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    job_data = job.to_dict()
    analysis = analyze_job(job_data)

    tracker = JobTracker()
    tracker.update_job_score(job.id, analysis.get("score"), str(analysis))
    tracker.update_job_status(job.id, "evaluated")

    return jsonify(analysis)


@bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
def apply_to_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    tracker = JobTracker()
    application = tracker.create_application(job.id)

    return jsonify(application.to_dict())


@bp.route("/search", methods=["POST"])
def search():
    data = request.json or {}
    keywords = data.get("keywords")
    locations = data.get("locations")
    portals = data.get("portals")

    raw_jobs = search_jobs(keywords, locations, portals)

    tracker = JobTracker()
    for raw_job in raw_jobs:
        job_data = format_job_data(raw_job)
        tracker.add_job(job_data)

    return jsonify({"found": len(raw_jobs), "jobs": raw_jobs[:10]})


@bp.route("/search/remote", methods=["POST"])
def search_remote():
    data = request.json or {}
    keywords = data.get("keywords")

    raw_jobs = search_remote_jobs(keywords)

    tracker = JobTracker()
    for raw_job in raw_jobs:
        job_data = format_job_data(raw_job)
        tracker.add_job(job_data)

    return jsonify({"found": len(raw_jobs), "jobs": raw_jobs[:10]})


@bp.route("/applications", methods=["GET"])
def get_applications():
    status = request.args.get("status")
    query = Application.query
    if status:
        query = query.filter_by(status=status)

    applications = query.order_by(Application.created_at.desc()).all()
    return jsonify([app.to_dict() for app in applications])


@bp.route("/stats", methods=["GET"])
def get_stats():
    tracker = JobTracker()
    stats = tracker.get_stats()
    return jsonify(stats)


@bp.route("/cvs", methods=["GET"])
def get_cvs():
    cvs = CV.query.all()
    return jsonify([cv.to_dict() for cv in cvs])


@bp.route("/cvs", methods=["POST"])
def create_cv():
    data = request.json

    cv = CV(
        name=data.get("name"),
        content=data.get("content"),
        base_cv=data.get("base_cv", False),
    )

    db.session.add(cv)
    db.session.commit()

    return jsonify(cv.to_dict()), 201


@bp.route("/cvs/<int:cv_id>", methods=["GET"])
def get_cv(cv_id):
    cv = CV.query.get(cv_id)
    if not cv:
        return jsonify({"error": "CV not found"}), 404
    return jsonify(cv.to_dict())


@bp.route("/cover-letter/<int:job_id>", methods=["GET"])
def get_cover_letter(job_id):
    cover_letter = generate_cover_letter_for_job(job_id)
    if not cover_letter:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"cover_letter": cover_letter})


@bp.route("/cover-letter/<int:job_id>/save", methods=["POST"])
def save_cover_letter_endpoint(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    cover_letter = generate_cover_letter_for_job(job_id)
    filepath = save_cover_letter(cover_letter, job.company, job.title)

    return jsonify({"saved": True, "path": filepath})


@bp.route("/interview-prep/<int:job_id>", methods=["GET"])
def get_interview_prep(job_id):
    prep = generate_interviewPrep_for_job(job_id)
    if not prep:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(prep)


@bp.route("/practice-interview", methods=["POST"])
def practice_interview_endpoint():
    data = request.json or {}
    topic = data.get("topic", "software engineer")
    difficulty = data.get("difficulty", "medium")

    result = practice_interview(topic, difficulty)
    return jsonify(result)


@bp.route("/salary-insights", methods=["GET"])
def salary_insights_endpoint():
    job_title = request.args.get("job_title", "software engineer")
    location = request.args.get("location", "Remote")

    insights = get_salary_insights(job_title, location)
    return jsonify(insights)


@bp.route("/apply/queue/<int:job_id>", methods=["POST"])
def queue_job_application(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    application = queue_application(job_id)
    if not application:
        return jsonify({"error": "Could not create application"}), 500

    return jsonify(application.to_dict()), 201


@bp.route("/apply/approve/<int:application_id>", methods=["POST"])
def approve_job_application(application_id):
    application = approve_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    return jsonify(application.to_dict())


@bp.route("/apply/reject/<int:application_id>", methods=["POST"])
def reject_job_application(application_id):
    data = request.json or {}
    reason = data.get("reason", "Rejected by user")

    application = reject_application(application_id, reason)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    return jsonify(application.to_dict())


@bp.route("/apply/run", methods=["POST"])
def run_apply_endpoint():
    results = run_auto_apply()
    return jsonify({"processed": len(results), "results": results})


@bp.route("/ai/analyze/<int:job_id>", methods=["GET"])
def ai_analyze_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    cv = CV.query.filter_by(base_cv=True).first()
    cv_content = ""
    if cv and cv.content:
        cv_content = cv.content

    job_data = job.to_dict()
    analysis = analyze_job_with_ai(job_data, {"cv_content": cv_content})

    return jsonify(analysis)


@bp.route("/ai/ats-keywords/<int:job_id>", methods=["GET"])
def get_ats_keywords(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    keywords = extract_ats_keywords(job.description)
    return jsonify({"keywords": keywords})


@bp.route("/ai/match/<int:job_id>", methods=["GET"])
def match_profile(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    cv = CV.query.filter_by(base_cv=True).first()
    cv_content = cv.content if cv and cv.content else ""

    job_data = job.to_dict()
    match = compare_with_profile(job_data, cv_content)

    return jsonify(match)


@bp.route("/ai/cover-letter/<int:job_id>", methods=["GET"])
def ai_cover_letter(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    cv = CV.query.filter_by(base_cv=True).first()
    profile_data = {
        "name": "Candidate",
        "experience_summary": cv.content if cv and cv.content else "",
    }

    job_data = job.to_dict()
    cover_letter = generate_cover_letter_with_ai(job_data, profile_data)

    return jsonify({"cover_letter": cover_letter})


@bp.route("/ai/interview-questions/<int:job_id>", methods=["GET"])
def ai_interview_questions(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    cv = CV.query.filter_by(base_cv=True).first()
    profile_data = {"experience_summary": cv.content if cv and cv.content else ""}

    job_data = job.to_dict()
    questions = generate_interview_questions(job_data, profile_data)

    return jsonify({"questions": questions})


@bp.route("/ai/chat", methods=["POST"])
def ai_chat():
    data = request.json or {}
    prompt = data.get("prompt", "")
    context = data.get("context", "")

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    response = chat_with_ai(prompt, context)
    return jsonify({"response": response})


@bp.route("/sheets/add", methods=["POST"])
def sheets_add():
    data = request.json or {}
    job_data = {
        "company": data.get("company", ""),
        "title": data.get("title", ""),
        "location": data.get("location", ""),
        "portal": data.get("portal", ""),
        "salary": data.get("salary", ""),
        "url": data.get("url", ""),
    }
    app_data = {
        "status": data.get("status", "pending"),
        "cv_path": data.get("cv_path", ""),
        "notes": data.get("notes", ""),
    }

    result = add_to_sheets(job_data, app_data)
    return jsonify({"success": result})


@bp.route("/sheets/update", methods=["POST"])
def sheets_update():
    data = request.json or {}
    company = data.get("company", "")
    title = data.get("title", "")
    status = data.get("status", "")
    notes = data.get("notes", "")

    if not company or not title:
        return jsonify({"error": "company and title required"}), 400

    result = update_sheets_status(company, title, status, notes)
    return jsonify({"success": result})


@bp.route("/sheets/stats", methods=["GET"])
def sheets_stats():
    stats = get_sheets_stats()
    return jsonify(stats)


@bp.route("/sheets/sync", methods=["POST"])
def sheets_sync():
    result = sync_sheets()
    return jsonify({"success": result})


@bp.route("/sheets/all", methods=["GET"])
def sheets_all():
    records = get_all_from_sheets()
    return jsonify({"applications": records})


@bp.route("/tracker/add", methods=["POST"])
def tracker_add():
    data = request.json or {}
    job_data = {
        "company": data.get("company", ""),
        "title": data.get("title", ""),
        "location": data.get("location", ""),
        "portal": data.get("portal", ""),
        "salary": data.get("salary", ""),
        "url": data.get("url", ""),
    }
    app_data = {
        "status": data.get("status", "pending"),
        "cv_path": data.get("cv_path", ""),
        "notes": data.get("notes", ""),
    }

    result = add_application(job_data, app_data)
    return jsonify({"success": result})


@bp.route("/tracker/update", methods=["POST"])
def tracker_update():
    data = request.json or {}
    company = data.get("company", "")
    title = data.get("title", "")
    status = data.get("status", "")
    notes = data.get("notes", "")

    if not company or not title:
        return jsonify({"error": "company and title required"}), 400

    result = update_tracker_status(company, title, status, notes)
    return jsonify({"success": result})


@bp.route("/tracker/stats", methods=["GET"])
def tracker_stats():
    stats = get_tracker_stats()
    return jsonify(stats)


@bp.route("/tracker/sync", methods=["POST"])
def tracker_sync():
    result = sync_from_db()
    return jsonify({"success": result})


@bp.route("/tracker/all", methods=["GET"])
def tracker_all():
    records = get_all_tracker()
    return jsonify({"applications": records})


@bp.route("/ranking/company/<company_name>", methods=["GET"])
def company_ranking(company_name):
    rank = get_company_ranking(company_name)
    return jsonify(rank)


@bp.route("/ranking/companies", methods=["POST"])
def companies_ranking():
    data = request.json or {}
    companies = data.get("companies", [])
    ranked = rank_companies(companies)
    return jsonify({"ranked": ranked})


@bp.route("/predict/success", methods=["POST"])
def predict_success_endpoint():
    data = request.json or {}
    job_data = data.get("job_data", {})
    history = data.get("history", {})

    result = predict_success(job_data, history)
    return jsonify(result)


@bp.route("/interview/response", methods=["POST"])
def interview_response():
    data = request.json or {}
    question = data.get("question", "")
    context = data.get("context", "")

    if not question:
        return jsonify({"error": "question required"}), 400

    response = generate_interview_response(question, context)
    return jsonify({"response": response})


@bp.route("/interview/cheatsheet", methods=["POST"])
def interview_cheatsheet():
    data = request.json or {}
    job_description = data.get("job_description", "")

    cheatsheet = generate_interview_cheatsheet(job_description)
    return jsonify(cheatsheet)


@bp.route("/email/followup", methods=["POST"])
def followup_email():
    data = request.json or {}
    email_type = data.get("type", "after_apply")
    company = data.get("company", "")
    position = data.get("position", "")
    context = data.get("context", "")

    email = generate_follow_up_email(email_type, company, position, context)
    return jsonify({"email": email})


@bp.route("/apply/dashboard", methods=["GET"])
def apply_dashboard():
    stats = get_dashboard_stats()
    return jsonify(stats)
