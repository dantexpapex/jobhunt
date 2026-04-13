import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.scraper import search_remote_jobs, format_job_data
from core.ats_optimizer import (
    extract_ats_keywords,
    optimize_for_ats,
    calculate_ats_score,
    generate_ats_tips,
)
from core.local_tracker import add_application
from core.cv_manager import CVManager
from config import Config


def run_full_pipeline():
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETO CON ATS")
    logger.info("=" * 60)

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
        logger.error(f"Error: {e}")
        raw_jobs = []

    # 2. ANALIZAR CADA JOB
    logger.info("2. Analizando trabajos (ATS + Match)...")

    cv_manager = CVManager()
    base_cv = cv_manager.available_cvs[0] if cv_manager.available_cvs else None

    jobs_to_queue = []

    for raw_job in raw_jobs[:15]:
        try:
            job_data = format_job_data(raw_job)
            job_description = job_data.get("description", "")

            stats["analyzed"] += 1

            # Obtener keywords ATS
            ats_keywords = extract_ats_keywords(job_description)

            # Score básico por keywords
            keyword_count = len(ats_keywords)
            base_score = min(100, 50 + (keyword_count * 3))

            ats_score = 0
            if base_cv:
                try:
                    cv_text = cv_manager.extract_content_from_docx(base_cv["path"])
                    result = optimize_for_ats(cv_text, job_description)
                    ats_score = result.get("score", base_score)
                except Exception as e:
                    logger.error(f"ATS error: {e}")
                    ats_score = base_score
            else:
                ats_score = base_score

            logger.info(f"   - {job_data['title'][:30]} @ {job_data['company'][:15]}")
            logger.info(f"     ATS Keywords: {keyword_count} | ATS Score: {ats_score}")

            # Filtrar por ATS score (>70)
            if ats_score >= 70:
                stats["matched"] += 1
                jobs_to_queue.append(
                    {
                        "job": job_data,
                        "ats_score": ats_score,
                        "keywords": [kw["keyword"] for kw in ats_keywords],
                    }
                )
                logger.info(f"     ✓ MATCH! (ATS: {ats_score}%)")

        except Exception as e:
            logger.error(f"Error: {e}")

    # 3. GUARDAR EN TRACKER
    logger.info("3. Guardando en tracker...")
    for item in jobs_to_queue:
        job = item["job"]
        tracker_data = {
            "company": job["company"],
            "title": job["title"],
            "location": job["location"],
            "portal": job["portal"],
            "salary": str(job.get("salary", "")),
            "url": job["url"],
        }

        ats_keywords_str = ", ".join(item["keywords"][:10])
        app_data = {
            "status": "pending_review",
            "notes": f"ATS: {item['ats_score']}% | Keywords: {ats_keywords_str}",
        }

        result = add_application(tracker_data, app_data)
        if result:
            stats["queued"] += 1

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETO")
    logger.info("=" * 60)
    logger.info(f"Jobs encontrados: {stats['scraped']}")
    logger.info(f"Jobs analizados: {stats['analyzed']}")
    logger.info(f"Matches ATS (>70%): {stats['matched']}")
    logger.info(f"En cola para revisar: {stats['queued']}")
    logger.info("=" * 60)

    return stats


if __name__ == "__main__":
    result = run_full_pipeline()

    print("\n" + "=" * 60)
    print("RESULTADOS FINALES:")
    print("=" * 60)
    print(f"Jobs encontrados: {result.get('scraped', 0)}")
    print(f"Jobs analizados: {result.get('analyzed', 0)}")
    print(f"Matches ATS (>70%): {result.get('matched', 0)}")
    print(f"En cola para revisar: {result.get('queued', 0)}")
    print("=" * 60)
