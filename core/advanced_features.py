import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

COMPANY_RANKING_CRITERIA = {
    "salary": 25,
    "culture": 20,
    "growth": 20,
    "remote_friendly": 15,
    "benefits": 10,
    "interview_difficulty": 10,
}

COMPANY_DATABASE = {
    "FAANG": {
        "name": "FAANG (Meta, Apple, Amazon, Netflix, Google)",
        "salary": 95,
        "culture": 90,
        "growth": 85,
        "remote_friendly": 70,
        "benefits": 95,
        "interview_difficulty": 95,
    },
    " Startups": {
        "name": "Startups Series A-D",
        "salary": 75,
        "culture": 85,
        "growth": 90,
        "remote_friendly": 95,
        "benefits": 60,
        "interview_difficulty": 70,
    },
    "Tech Corp": {
        "name": "Tech Corporations (non-FAANG)",
        "salary": 80,
        "culture": 80,
        "growth": 75,
        "remote_friendly": 80,
        "benefits": 85,
        "interview_difficulty": 80,
    },
    "Remote-First": {
        "name": "Remote-First Companies",
        "salary": 70,
        "culture": 85,
        "growth": 70,
        "remote_friendly": 100,
        "benefits": 75,
        "interview_difficulty": 60,
    },
}


def get_company_ranking(company_name, external_data=None):
    company_lower = company_name.lower()

    for tier, data in COMPANY_DATABASE.items():
        if tier.lower() in company_lower:
            return calculate_rank(data, external_data)

    return calculate_rank(
        {
            "salary": 50,
            "culture": 50,
            "growth": 50,
            "remote_friendly": 50,
            "benefits": 50,
            "interview_difficulty": 50,
        },
        external_data,
    )


def calculate_rank(data, external_data=None):
    score = 0

    for criterion, weight in COMPANY_RANKING_CRITERIA.items():
        score += data.get(criterion, 50) * weight / 100

    tier = "B"
    if score >= 85:
        tier = "S"
    elif score >= 75:
        tier = "A"
    elif score >= 60:
        tier = "C"
    elif score < 40:
        tier = "D"

    return {
        "company_tier": tier,
        "overall_score": round(score, 1),
        "salary_score": data.get("salary", 50),
        "culture_score": data.get("culture", 50),
        "growth_score": data.get("growth", 50),
        "remote_score": data.get("remote_friendly", 50),
        "benefits_score": data.get("benefits", 50),
        "difficulty_score": data.get("interview_difficulty", 50),
    }


def rank_companies(companies):
    ranked = []

    for company in companies:
        rank = get_company_ranking(company.get("name", ""))
        ranked.append(
            {
                "name": company.get("name", ""),
                "tier": rank["company_tier"],
                "score": rank["overall_score"],
            }
        )

    ranked.sort(key=lambda x: x["score"], reverse=True)

    for i, comp in enumerate(ranked):
        comp["rank"] = i + 1

    return ranked


def predict_success(job_data, application_history):
    from core.ai_engine import analyze_job_with_ai

    factors = {
        "keywords_match": 0,
        "experience_match": 0,
        "skills_match": 0,
        "company_ranking": 0,
    }

    job_description = job_data.get("description", "")
    ats_keywords = extract_simple_keywords(job_description)

    keyword_matches = len([kw for kw in ats_keywords if kw in job_description.lower()])
    factors["keywords_match"] = min(100, keyword_matches * 15)

    company = job_data.get("company", "")
    rank = get_company_ranking(company)
    factors["company_ranking"] = rank["overall_score"]

    base_success = (
        factors["keywords_match"] * 0.4
        + factors["experience_match"] * 0.2
        + factors["skills_match"] * 0.2
        + factors["company_ranking"] * 0.2
    )

    history_factor = calculate_history_factor(application_history)
    predicted_success = min(100, base_success * history_factor)

    return {
        "predicted_success": round(predicted_success, 1),
        "factors": factors,
        "recommendation": get_recommendation(predicted_success),
    }


def calculate_history_factor(history):
    if not history:
        return 0.8

    applied = history.get("applied", 0)
    interview = history.get("interview", 0)

    if applied == 0:
        return 0.7

    rate = interview / applied

    if rate > 0.3:
        return 1.2
    elif rate > 0.15:
        return 1.0
    elif rate > 0.05:
        return 0.8
    else:
        return 0.6


def get_recommendation(score):
    if score >= 80:
        return "Strong apply - High success probability"
    elif score >= 60:
        return "Good match - Worth applying"
    elif score >= 40:
        return "Consider carefully - May need extra effort"
    else:
        return "Low probability - Only if desperate"


def extract_simple_keywords(text):
    if not text:
        return []

    keywords = []
    tech_terms = [
        "python",
        "java",
        "javascript",
        "react",
        "angular",
        "vue",
        "node",
        "django",
        "flask",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "sql",
        "postgresql",
        "mongodb",
        "redis",
        "machine learning",
        "ai",
    ]

    text_lower = text.lower()
    for term in tech_terms:
        if term in text_lower:
            keywords.append(term)

    return keywords
