import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = (
        os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR}/data/jobs.db"
    )

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

    SEARCH_KEYWORDS = os.environ.get(
        "SEARCH_KEYWORDS", "software engineer,python,backend"
    ).split(",")
    SEARCH_LOCATIONS = os.environ.get("SEARCH_LOCATIONS", "Remote,United States").split(
        ","
    )
    SEARCH_PORTALS = os.environ.get(
        "SEARCH_PORTALS", "linkedin,indeed,glassdoor"
    ).split(",")

    REMOTE_PORTALS = os.environ.get(
        "REMOTE_PORTALS", "remoteok,weworkremotely,hackernews,angellist"
    ).split(",")

    AUTO_APPLY_ENABLED = os.environ.get("AUTO_APPLY_ENABLED", "false").lower() == "true"
    APPLY_THRESHOLD = int(os.environ.get("APPLY_THRESHOLD", 70))
    MAX_APPLICATIONS_PER_DAY = int(os.environ.get("MAX_APPLICATIONS_PER_DAY", 50))
    MIN_DELAY_BETWEEN_APPLIES = int(os.environ.get("MIN_DELAY_BETWEEN_APPLIES", 300))

    SCORING_WEIGHTS = {
        "salary": 0.20,
        "remote": 0.15,
        "tech_stack": 0.25,
        "experience": 0.15,
        "company": 0.10,
        "fit_score": 0.15,
    }

    REVIEW_THRESHOLD = 50
    REJECT_THRESHOLD = 50

    LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD", "")

    SCHEDULER_INTERVAL_HOURS = int(os.environ.get("SCHEDULER_INTERVAL_HOURS", 6))

    JOB_STATUS_NEW = "new"
    JOB_STATUS_EVALUATED = "evaluated"
    JOB_STATUS_APPLIED = "applied"
    JOB_STATUS_INTERVIEW = "interview"
    JOB_STATUS_REJECTED = "rejected"
    JOB_STATUS_OFFER = "offer"
