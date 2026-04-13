import google.generativeai as genai
from config import Config
import json
import logging
import random

logger = logging.getLogger(__name__)

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

COMMON_QUESTIONS = [
    "Tell me about yourself.",
    "Why are you interested in this position?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?",
    "Why should we hire you?",
    "Describe a challenging project you worked on.",
    "How do you handle conflict with coworkers?",
    "What are your salary expectations?",
    "Do you have any questions for us?",
]

TECH_QUESTIONS = [
    "Explain the difference between REST and GraphQL.",
    "What is your tech stack and why?",
    "Describe your experience with Agile/Scrum.",
    "How do you optimize database queries?",
    "Explain CI/CD pipelines.",
    "What design patterns do you use?",
    "How do you handle technical debt?",
    "Describe your debugging process.",
]


def generate_interview_questions(job_data, num_questions=10):
    if not Config.GEMINI_API_KEY:
        return get_default_questions(job_data, num_questions)

    prompt = build_questions_prompt(job_data, num_questions)

    try:
        response = model.generate_content(prompt)
        return parse_questions_response(response.text)
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return get_default_questions(job_data, num_questions)


def build_questions_prompt(job_data, num_questions):
    return f"""Generate {num_questions} interview questions for a {job_data.get("title", "software engineer")} position at {job_data.get("company", "a tech company")}.

Job Description: {job_data.get("description", "")[:1500]}

Include:
- 5 general/behavioral questions
- 5 technical questions relevant to the role

Return ONLY a JSON array like this (no other text):
["Question 1?", "Question 2?", ...]"""


def parse_questions_response(response_text):
    try:
        import re

        json_str = response_text.strip()
        if "```json" in json_str:
            json_str = json_str.replace("```json", "").replace("```", "")
        elif "```" in json_str:
            json_str = json_str.replace("```", "")

        questions = json.loads(json_str)
        if isinstance(questions, list):
            return questions
    except Exception as e:
        logger.error(f"Error parsing questions: {e}")

    return get_default_questions({}, 10)


def get_default_questions(job_data, num_questions=10):
    all_questions = COMMON_QUESTIONS + TECH_QUESTIONS
    selected = random.sample(all_questions, min(num_questions, len(all_questions)))
    return selected


def generate_answer(question, job_data, personal_info):
    if not Config.GEMINI_API_KEY:
        return get_default_answer(question)

    prompt = build_answer_prompt(question, job_data, personal_info)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return get_default_answer(question)


def build_answer_prompt(question, job_data, personal_info):
    company = job_data.get("company", "the company")
    title = job_data.get("title", "the position")

    return f"""Write a professional answer to this interview question for a {title} position at {company}.

Question: {question}

Candidate background: {personal_info.get("experience_summary", "Experienced software engineer")}

Provide a 2-3 sentence answer that is:
- Concise and specific
- Uses the STAR method when applicable
- Highlights relevant experience

Return ONLY the answer (no explanations)."""


def get_default_answer(question):
    return "I would address this by focusing on my relevant experience and demonstrating how my skills align with the position requirements. I'm committed to continuous growth and contributing to team success."


def generate_interviewPrep_for_job(job_id):
    from models.job import Job
    from core.tracker import get_base_cv

    job = Job.query.get(job_id)
    if not job:
        return None

    cv = get_base_cv()
    personal_info = json.loads(cv.content) if cv and cv.content else {}

    job_data = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
    }

    questions = generate_interview_questions(job_data)
    answers = {}

    for q in questions:
        answers[q] = generate_answer(q, job_data, personal_info)

    return {
        "questions": questions,
        "answers": answers,
        "job_title": job.title,
        "company": job.company,
    }


def practice_interview(topic, difficulty="medium"):
    if not Config.GEMINI_API_KEY:
        return {
            "scenario": f"Practice interview for {topic} position",
            "tips": ["Be confident", "Use STAR method", "Ask clarifying questions"],
        }

    prompt = f"""Generate a mock interview scenario for a {topic} position at {difficulty} difficulty level.

Include:
1. A brief scenario/context
2. 3-5 follow-up questions
3. Key things the interviewer is looking for
4. Tips for answering well

Return as JSON:
{{
    "scenario": "...",
    "questions": [...],
    "what_to_look_for": [...],
    "tips": [...]
}}"""

    try:
        response = model.generate_content(prompt)
        import re

        json_str = response.text.strip()
        if "```json" in json_str:
            json_str = json_str.replace("```json", "").replace("```", "")

        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error generating practice interview: {e}")
        return {
            "scenario": f"Practice interview for {topic}",
            "tips": ["Be confident", "Use STAR method"],
        }


def get_salary_insights(job_title, location):
    if not Config.GEMINI_API_KEY:
        return get_default_salary_insights(job_title, location)

    prompt = f"""Provide salary insights for a {job_title} position in {location}.

Include:
- Salary range (low, mid, high)
- Key factors affecting salary
- Negotiation tips

Return as JSON (no extra text):
{{
    "range": "$X - $Y",
    "factors": [...],
    "negotiation_tips": [...]
}}"""

    try:
        response = model.generate_content(prompt)
        import re

        json_str = response.text.strip()
        if "```json" in json_str:
            json_str = json_str.replace("```json", "").replace("```", "")

        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error getting salary insights: {e}")
        return get_default_salary_insights(job_title, location)


def get_default_salary_insights(job_title, location):
    return {
        "range": "$80,000 - $150,000",
        "factors": ["Experience", "Skills", "Company size", "Location"],
        "negotiation_tips": [
            "Research market rates",
            "Practice your pitch",
            "Be confident",
        ],
    }
