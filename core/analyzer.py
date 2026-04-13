from google import genai
from config import Config
import json
import logging

logger = logging.getLogger(__name__)

if Config.GEMINI_API_KEY:
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
else:
    client = None


def analyze_job(job_data):
    if not client:
        return get_default_score()

    prompt = build_analysis_prompt(job_data)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        score_data = parse_analysis_response(response.text)
        return score_data
    except Exception as e:
        logger.error(f"Error analyzing job: {e}")
        return get_default_score()


def build_analysis_prompt(job_data):
    return f"""Analyze this job posting and provide a score (0-100) based on the following dimensions:

Job Title: {job_data.get("title", "")}
Company: {job_data.get("company", "")}
Location: {job_data.get("location", "")}
Description: {job_data.get("description", "")[:2000]}

Rate each dimension (0-100) and provide the total score:
A - Salary: Is the salary competitive? (estimate if not provided)
B - Remote: Is it remote/hybrid/onsite?
C - Tech Stack: Do the required technologies match?
D - Experience: Is the experience level appropriate?
E - Company: Is the company desirable?
F - Fit: Overall match score

Return ONLY a JSON object like this (no other text):
{{
    "score": 75,
    "salary_score": 80,
    "remote_score": 90,
    "tech_stack_score": 70,
    "experience_score": 75,
    "company_score": 70,
    "fit_score": 75,
    "reasoning": "Brief explanation"
}}"""


def parse_analysis_response(response_text):
    try:
        json_str = response_text.strip()
        if "```json" in json_str:
            json_str = json_str.replace("```json", "").replace("```", "")
        elif "```" in json_str:
            json_str = json_str.replace("```", "")

        data = json.loads(json_str.strip())
        return data
    except Exception as e:
        logger.error(f"Error parsing analysis: {e}")
        return get_default_score()


def get_default_score():
    return {
        "score": 50,
        "salary_score": 50,
        "remote_score": 50,
        "tech_stack_score": 50,
        "experience_score": 50,
        "company_score": 50,
        "fit_score": 50,
        "reasoning": "Default score - could not analyze",
    }


def calculate_overall_score(scores):
    weights = Config.SCORING_WEIGHTS
    total = (
        scores.get("salary_score", 0) * weights["salary"]
        + scores.get("remote_score", 0) * weights["remote"]
        + scores.get("tech_stack_score", 0) * weights["tech_stack"]
        + scores.get("experience_score", 0) * weights["experience"]
        + scores.get("company_score", 0) * weights["company"]
        + scores.get("fit_score", 0) * weights["fit_score"]
    )
    return round(total, 2)


def should_apply(score):
    return score >= Config.APPLY_THRESHOLD


def should_review(score):
    return score >= Config.REVIEW_THRESHOLD and score < Config.APPLY_THRESHOLD
