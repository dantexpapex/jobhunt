import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import gspread
    from gspread import Client as GSpreadClient

    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logger.warning("gspread not installed. Install with: pip install gspread")

from config import Config


class SheetsTracker:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.worksheet = None

        if not GSPREAD_AVAILABLE:
            logger.error("gspread not available. Install: pip install gspread")
            return

        try:
            self._authenticate()
        except Exception as e:
            logger.error(f"Sheets auth error: {e}")

    def _authenticate(self):
        credentials_path = os.environ.get("GOOGLE_SHEETS_CREDS")

        if credentials_path and os.path.exists(credentials_path):
            self.client = gspread.service_account(credentials_path)
        else:
            creds_json = os.environ.get("GOOGLE_SHEETS_CREDS_JSON")
            if creds_json:
                import json
                from gspread import authorize
                from google.auth import credentials
                from google.oauth2 import service_account

                creds_dict = json.loads(creds_json)
                self.client = gspread.service_account.from_dict(creds_dict)
            else:
                logger.warning(
                    "No Google Sheets credentials found. Set GOOGLE_SHEETS_CREDS or GOOGLE_SHEETS_CREDS_JSON"
                )

    def open_spreadsheet(self, spreadsheet_name=None):
        if not self.client:
            return None

        name = spreadsheet_name or os.environ.get(
            "GOOGLE_SHEETS_NAME", "JobHunt Tracker"
        )

        try:
            self.spreadsheet = self.client.open(name)
            self.worksheet = self.spreadsheet.sheet1
            return self.worksheet
        except gspread.SpreadsheetNotFound:
            self.spreadsheet = self.client.create(name)
            self.worksheet = self.spreadsheet.sheet1
            self._initialize_headers()
            return self.worksheet

    def _initialize_headers(self):
        headers = [
            "Fecha",
            "Empresa",
            "Puesto",
            "Ubicación",
            "Portal",
            "Salario",
            "Estado",
            "CV Enviado",
            "Fecha Aplicación",
            "Respuesta",
            "Notas",
            "URL",
        ]
        self.worksheet.append_row(headers)

    def add_application(self, job_data, application_data=None):
        if not self.worksheet:
            self.open_spreadsheet()

        if not self.worksheet:
            return None

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        row = [
            now,
            job_data.get("company", ""),
            job_data.get("title", ""),
            job_data.get("location", ""),
            job_data.get("portal", ""),
            job_data.get("salary", ""),
            application_data.get("status", "pending")
            if application_data
            else "pending",
            "Sí" if application_data and application_data.get("cv_path") else "No",
            now if application_data else "",
            application_data.get("response_received", "No")
            if application_data
            else "No",
            application_data.get("notes", "") if application_data else "",
            job_data.get("url", ""),
        ]

        try:
            self.worksheet.append_row(row)
            logger.info(
                f"Added to Google Sheets: {job_data.get('company')} - {job_data.get('title')}"
            )
            return True
        except Exception as e:
            logger.error(f"Error adding to sheets: {e}")
            return False

    def update_status(self, company, title, new_status, notes=None):
        if not self.worksheet:
            self.open_spreadsheet()

        if not self.worksheet:
            return False

        try:
            records = self.worksheet.get_all_records()

            for i, record in enumerate(records, start=2):
                if record.get("Empresa") == company and record.get("Puesto") == title:
                    self.worksheet.update(f"G{i}", new_status)
                    if notes:
                        self.worksheet.update(f"K{i}", notes)
                    return True

            return False
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False

    def get_all_applications(self):
        if not self.worksheet:
            self.open_spreadsheet()

        if not self.worksheet:
            return []

        try:
            records = self.worksheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            return []

    def get_stats(self):
        records = self.get_all_applications()

        stats = {
            "total": len(records),
            "pending": 0,
            "applied": 0,
            "interview": 0,
            "rejected": 0,
            "offer": 0,
        }

        for record in records:
            status = record.get("Estado", "").lower()
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

    def sync_from_db(self):
        from models.database import db
        from models.job import Job
        from models.application import Application

        if not self.worksheet:
            self.open_spreadsheet()

        if not self.worksheet:
            return False

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
                    "response_received": "Sí" if app.response_received else "No",
                    "notes": app.notes or "",
                }

                self.add_application(job_data, app_data)

            return True
        except Exception as e:
            logger.error(f"Error syncing from DB: {e}")
            return False


sheets_tracker = SheetsTracker()


def add_to_sheets(job_data, application_data=None):
    return sheets_tracker.add_application(job_data, application_data)


def update_sheets_status(company, title, status, notes=None):
    return sheets_tracker.update_status(company, title, status, notes)


def get_sheets_stats():
    return sheets_tracker.get_stats()


def sync_sheets():
    return sheets_tracker.sync_from_db()


def get_all_from_sheets():
    return sheets_tracker.get_all_applications()
