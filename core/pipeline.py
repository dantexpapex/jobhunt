from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import Config
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_full_pipeline():
    """Pipeline completo automático"""
    from app import app, db
    from core.scraper import search_remote_jobs, format_job_data
    from core.analyzer import analyze_job
    from core.hybrid_apply import HybridAutoApplier
    from core.ai_engine import analyze_job_with_ai
    from core.local_tracker import add_application
    from models.job import Job
    from config import Config

    with app.app_context():
        return _run_pipeline_inner()


def _run_pipeline_inner():
    logger.info("=" * 50)
    logger.info("INICIANDO PIPELINE COMPLETO")
    logger.info("=" * 50)

    stats = {
        "scraped": 0,
        "analyzed": 0,
        "matched": 0,
        "queued": 0,
    }

    # 1. BUSCAR TRABAJOS
    logger.info("1. Buscando trabajos...")
    try:
        raw_jobs = search_remote_jobs(Config.SEARCH_KEYWORDS, num_jobs=20)
        stats["scraped"] = len(raw_jobs)
        logger.info(f"   Encontrados: {len(raw_jobs)} jobs")
    except Exception as e:
        logger.error(f"Error buscando: {e}")
        raw_jobs = []

    # 2. ANALIZAR Y FILTRAR
    logger.info("2. Analizando trabajos...")
    applier = HybridAutoApplier()

    for raw_job in raw_jobs[:10]:
        try:
            job_data = format_job_data(raw_job)

            existing = Job.query.filter_by(external_id=job_data["external_id"]).first()
            if existing:
                logger.info(f"   Job ya existe: {job_data['title']}")
                continue

            job = Job(
                external_id=job_data["external_id"],
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"],
                url=job_data["url"],
                portal=job_data["portal"],
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                remote_type=job_data.get("remote_type"),
                status="new",
            )
            db.session.add(job)
            db.session.commit()
            stats["analyzed"] += 1

            # 3. ANALIZAR CON IA
            try:
                analysis = analyze_job_with_ai(job_data)
                match_score = analysis.get("match_percentage", 0)
                job.score = analysis.get("score", 50)
                job.score_details = str(analysis)
            except:
                match_score = 50
                job.score = 50

            db.session.commit()

            # 4. FILTRAR POR MATCH (>70%)
            if match_score >= Config.APPLY_THRESHOLD:
                stats["matched"] += 1
                logger.info(f"   MATCH: {job.title} @ {job.company} ({match_score}%)")

                # 5. CREAR APLICACIÓN CON CV ADAPTADO
                app = applier.create_application(job.id, generate_docs=True)
                if app:
                    stats["queued"] += 1
                    logger.info(f"   COLA: {job.title} - pending_review")

                    # 6. GUARDAR EN TRACKER
                    tracker_data = {
                        "company": job.company,
                        "title": job.title,
                        "location": job.location,
                        "portal": job.portal,
                        "salary": f"${job.salary_min or ''} - ${job.salary_max or ''}",
                        "url": job.url,
                    }
                    app_data = {
                        "status": "pending_review",
                        "cv_path": app.cv_path,
                    }
                    add_application(tracker_data, app_data)

        except Exception as e:
            logger.error(f"Error procesando job: {e}")

    # 7. NOTIFICAR
    logger.info("=" * 50)
    logger.info(f"PIPELINE COMPLETO: {stats}")
    logger.info(f"   Jobs encontrados: {stats['scraped']}")
    logger.info(f"   Jobs analizados: {stats['analyzed']}")
    logger.info(f"   Matches (>70%): {stats['matched']}")
    logger.info(f"   En cola: {stats['queued']}")
    logger.info("=" * 50)

    if stats["queued"] > 0:
        notify_user(stats)

    return stats


def notify_user(stats):
    """Notificar al usuario"""
    from core.telegram_bot import notifier

    if not notifier or not notifier.bot:
        logger.info(f"📢 NUEVAS APLICACIONES: {stats['queued']}")
        return

    try:
        text = f"🤖 *JobHunt Pipeline Complete*\n\n"
        text += f"Jobs encontrados: {stats['scraped']}\n"
        text += f"Matches: {stats['matched']}\n"
        text += f"En cola para revisar: {stats['queued']}\n\n"
        text += "Revisa en: /applications"

        notifier.send_message(text)
    except Exception as e:
        logger.error(f"Error notificando: {e}")


def start_pipeline_scheduler():
    """Iniciar scheduler del pipeline"""
    if scheduler.running:
        logger.warning("Scheduler ya corriendo")
        return

    interval = int(Config.SCHEDULER_INTERVAL_HOURS or 6)

    scheduler.add_job(
        run_full_pipeline,
        trigger=IntervalTrigger(hours=interval),
        id="jobhunt_pipeline",
        name="JobHunt Full Pipeline",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Pipeline scheduler iniciado cada {interval} horas")


def stop_pipeline_scheduler():
    """Detener scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Pipeline scheduler detenido")


def run_pipeline_now():
    """Ejecutar pipeline manualmente"""
    logger.info("Ejecutando pipeline manualmente...")
    return run_full_pipeline()


if __name__ == "__main__":
    run_full_pipeline()
