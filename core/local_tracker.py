import os
import csv
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TRACKER_FILE = "data/tracker.csv"


class SimpleTracker:
    def __init__(self, filepath=TRACKER_FILE):
        self.filepath = filepath
        os.makedirs("data", exist_ok=True)
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.filepath):
            headers = [
                "Fecha",
                "Empresa",
                "Puesto",
                "Ubicacion",
                "Portal",
                "Salario",
                "Estado",
                "CV Enviado",
                "Fecha Aplicacion",
                "Respuesta",
                "Notas",
                "URL",
            ]
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def add_application(self, job_data, app_data=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        row = [
            now,
            job_data.get("company", ""),
            job_data.get("title", ""),
            job_data.get("location", ""),
            job_data.get("portal", ""),
            job_data.get("salary", ""),
            app_data.get("status", "pending") if app_data else "pending",
            "Si" if app_data and app_data.get("cv_path") else "No",
            now if app_data and app_data.get("status") == "applied" else "",
            app_data.get("response_received", "No") if app_data else "No",
            app_data.get("notes", "") if app_data else "",
            job_data.get("url", ""),
        ]

        try:
            with open(self.filepath, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            logger.error(f"Error adding: {e}")
            return False

    def update_status(self, company, title, new_status, notes=None):
        rows = []
        updated = False

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)

            for i, row in enumerate(rows):
                if len(row) > 1 and row[1] == company and row[2] == title:
                    rows[i][6] = new_status
                    if notes:
                        rows[i][10] = notes
                    updated = True

            if updated:
                with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)

            return updated
        except Exception as e:
            logger.error(f"Error updating: {e}")
            return False

    def get_all(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except:
            return []

    def get_stats(self):
        apps = self.get_all()

        stats = {
            "total": len(apps),
            "pending": 0,
            "applied": 0,
            "interview": 0,
            "rejected": 0,
            "offer": 0,
        }

        for app in apps:
            status = (app.get("Estado") or "").lower()
            if "pending" in status:
                stats["pending"] += 1
            elif "applied" in status:
                stats["applied"] += 1
            elif "interview" in status:
                stats["interview"] += 1
            elif "rejected" in status:
                stats["rejected"] += 1
            elif "offer" in status:
                stats["offer"] += 1

        return stats


simple_tracker = SimpleTracker()


def add_application(job_data, app_data=None):
    return simple_tracker.add_application(job_data, app_data)


def update_tracker_status(company, title, status, notes=None):
    return simple_tracker.update_status(company, title, status, notes)


def get_tracker_stats():
    return simple_tracker.get_stats()


def get_all_tracker():
    return simple_tracker.get_all()


def sync_from_db():
    from models.database import db
    from models.job import Job
    from models.application import Application

    try:
        applications = Application.query.all()

        for app in applications:
            job = Job.query.get(app.job_id)
            if not job:
                continue

            job_data = {
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "portal": job.portal,
                "url": job.url,
            }

            app_data = {
                "status": app.status,
                "cv_path": app.cv_path,
                "response_received": "Si" if app.response_received else "No",
                "notes": app.notes or "",
            }

            add_application(job_data, app_data)

        return True
    except Exception as e:
        logger.error(f"Error syncing: {e}")
        return False
