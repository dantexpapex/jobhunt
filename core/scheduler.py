from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import Config
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    if scheduler.running:
        logger.warning("Scheduler already running")
        return

    scheduler.add_job(
        run_job_discovery,
        trigger=IntervalTrigger(hours=Config.SCHEDULER_INTERVAL_HOURS),
        id="job_discovery",
        name="Discover new jobs",
        replace_existing=True,
    )

    scheduler.add_job(
        run_applications,
        trigger=IntervalTrigger(hours=1),
        id="job_applications",
        name="Apply to qualified jobs",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def run_job_discovery():
    from core.scraper import search_jobs, format_job_data
    from core.tracker import JobTracker

    try:
        logger.info("Running job discovery...")
        raw_jobs = search_jobs()

        tracker = JobTracker()
        for raw_job in raw_jobs:
            job_data = format_job_data(raw_job)
            tracker.add_job(job_data)

        logger.info(f"Discovery complete: {len(raw_jobs)} jobs found")
    except Exception as e:
        logger.error(f"Error in job discovery: {e}")


def run_applications():
    from core.tracker import JobTracker

    if not Config.AUTO_APPLY_ENABLED:
        logger.info("Auto-apply disabled")
        return

    try:
        logger.info("Running job applications...")
        tracker = JobTracker()
        jobs = tracker.get_jobs_to_apply(Config.APPLY_THRESHOLD)

        if not jobs:
            logger.info("No jobs to apply")
            return

        from core.auto_applier import apply_with_delay

        applied_today = 0
        for job in jobs:
            if applied_today >= Config.MAX_APPLICATIONS_PER_DAY:
                break

            result = apply_with_delay(job.url, delay_seconds=5)
            if result:
                tracker.create_application(job.id)
                applied_today += 1

        logger.info(f"Applications complete: {applied_today} jobs applied")
    except Exception as e:
        logger.error(f"Error in applications: {e}")


def run_evaluation():
    from core.scraper import search_jobs, format_job_data
    from core.analyzer import analyze_job
    from core.tracker import JobTracker

    try:
        logger.info("Running job evaluation...")
        tracker = JobTracker()
        jobs = tracker.get_jobs_by_status("new")

        for job in jobs:
            job_data = job.__dict__.copy()
            if "_sa_instance_state" in job_data:
                del job_data["_sa_instance_state"]

            analysis = analyze_job(job_data)
            tracker.update_job_score(job.id, analysis.get("score"), str(analysis))
            tracker.update_job_status(job.id, "evaluated")

        logger.info(f"Evaluation complete: {len(jobs)} jobs evaluated")
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")


def trigger_discovery():
    run_job_discovery()


def trigger_applications():
    run_applications()


def trigger_evaluation():
    run_evaluation()
