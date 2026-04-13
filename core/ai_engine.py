import os
import json
from google import genai
from config import Config
import logging

logger = logging.getLogger(__name__)

if Config.GEMINI_API_KEY:
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
else:
    client = None


def analyze_job_with_ai(job_data, profile_data=None):
    if not client:
        return get_fallback_analysis(job_data)

    prompt = build_job_analysis_prompt(job_data, profile_data)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return parse_analysis_response(response.text)
    except Exception as e:
        logger.error(f"Error analyzing job with AI: {e}")
        return get_fallback_analysis(job_data)


def build_job_analysis_prompt(job_data, profile_data):
    title = job_data.get("title", "")
    company = job_data.get("company", "")
    description = job_data.get("description", "")[:3000]
    location = job_data.get("location", "")

    profile_info = ""
    if profile_data:
        profile_info = f"""
CANDIDATE PROFILE:
- Skills: {profile_data.get("skills", "")}
- Experience: {profile_data.get("experience_summary", "")}
- Languages: {profile_data.get("languages", "Spanish, English")}
"""

    return f"""You are an expert HR analyst. Analyze this job posting and provide a detailed report.

JOB POSTING:
- Title: {title}
- Company: {company}
- Location: {location}
- Description: {description}
{profile_info}

Provide JSON (no other text):
{{
    "score": 0-100,
    "salary_estimate": "$X - $Y",
    "remote_type": "remote/hybrid/onsite",
    "experience_level": "junior/mid/senior/lead",
    "ats_keywords": ["keyword1", "keyword2", ...],
    "missing_keywords": ["keyword1", ...],
    "match_percentage": 0-100,
    "strengths": ["strength1", ...],
    "weaknesses": ["weakness1", ...],
    "application_tips": ["tip1", ...],
    "cover_letter_talking_points": ["point1", ...],
    "reasoning": "brief explanation"
}}"""


def parse_analysis_response(response_text):
    try:
        text = response_text.strip()
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")

        data = json.loads(text.strip())
        return data
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return get_fallback_analysis({})


def get_fallback_analysis(job_data):
    return {
        "score": 50,
        "salary_estimate": "$50,000 - $100,000",
        "remote_type": "unknown",
        "experience_level": "mid",
        "ats_keywords": extract_basic_keywords(job_data.get("description", "")),
        "missing_keywords": [],
        "match_percentage": 50,
        "strengths": ["Relevant background"],
        "weaknesses": ["Need more info"],
        "application_tips": ["Customize your CV", "Add relevant keywords"],
        "cover_letter_talking_points": [
            "Express interest",
            "Highlight relevant skills",
        ],
        "reasoning": "Using basic analysis",
    }


def extract_basic_keywords(description):
    if not description:
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
        "fastapi",
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "git",
        "linux",
        "api",
        "rest",
        "graphql",
        "microservices",
        "agile",
        "scrum",
        "machine learning",
        "ai",
        "data analysis",
        "excel",
        "tableau",
        "html",
        "css",
        "typescript",
        "jquery",
        "bootstrap",
    ]

    desc_lower = description.lower()
    for term in tech_terms:
        if term in desc_lower:
            keywords.append(term)

    return keywords[:15]


def extract_ats_keywords(job_description):
    keywords = []

    sections = {
        "technical": [
            "python",
            "java",
            "sql",
            "aws",
            "docker",
            "kubernetes",
            "git",
            "linux",
            "api",
        ],
        "soft_skills": [
            "communication",
            "teamwork",
            "leadership",
            "problem solving",
            "collaboration",
        ],
        "methodologies": ["agile", "scrum", "kanban", "devops", "ci/cd"],
        "tools": ["jira", "confluence", "slack", "teams", "zoom", "notion"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "spring"],
        "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch"],
        "cloud": ["aws", "azure", "gcp", "ec2", "s3", "lambda"],
    }

    desc_lower = job_description.lower() if job_description else ""

    for category, terms in sections.items():
        for term in terms:
            if term in desc_lower:
                keywords.append({"keyword": term, "category": category})

    keywords.sort(key=lambda x: x["keyword"])
    return keywords


def compare_with_profile(job_data, cv_content):
    if not client:
        return compare_basic(job_data, cv_content)

    prompt = f"""Compare job requirements with candidate profile and provide match analysis.

JOB REQUIREMENTS:
{job_data.get("description", "")[:2000]}

CANDIDATE PROFILE:
{cv_content[:1500]}

Provide JSON:
{{
    "match_score": 0-100,
    "matching_skills": [...],
    "gap_skills": [...],
    "recommendations": [...]
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return compare_basic(job_data, cv_content)


def compare_basic(job_data, cv_content):
    job_kw = set(extract_basic_keywords(job_data.get("description", "")))
    cv_kw = set(extract_basic_keywords(cv_content))

    matching = job_kw & cv_kw
    gaps = job_kw - cv_kw

    match_score = len(matching) / len(job_kw) * 100 if job_kw else 50

    return {
        "match_score": round(match_score, 1),
        "matching_skills": list(matching),
        "gap_skills": list(gaps),
        "recommendations": [f"Add {s} to your CV" for s in gaps],
    }


def generate_cover_letter_with_ai(job_data, profile_data):
    if not client:
        return generate_basic_cover_letter(job_data, profile_data)

    prompt = f"""Write a professional cover letter (300 words max).

JOB: {job_data.get("title", "")} at {job_data.get("company", "")}
LOCATION: {job_data.get("location", "")}
DESCRIPTION: {job_data.get("description", "")[:1000]}

CANDIDATE:
Name: {profile_data.get("name", "Candidate")}
Background: {profile_data.get("experience_summary", "Experienced professional")}

Write in professional tone, highlighting relevant skills. Return ONLY the letter text."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return generate_basic_cover_letter(job_data, profile_data)


def generate_basic_cover_letter(job_data, profile_data):
    name = (
        profile_data.get("name", "Hiring Manager") if profile_data else "Hiring Manager"
    )
    company = job_data.get("company", "Company") if job_data else "Company"
    title = job_data.get("title", "Position") if job_data else "Position"

    return f"""Dear {name},

I am writing to express my strong interest in the {title} position at {company}.

With my background in software development and passion for creating efficient solutions, 
I believe I would be a valuable addition to your team.

I am excited about the opportunity to contribute to {company} and would welcome 
the chance to discuss how my skills align with your needs.

Thank you for considering my application.

Best regards"""


def generate_interview_questions(job_data, profile_data, num=10):
    if not client:
        return get_default_questions(num)

    prompt = f"""Generate {num} interview questions for a {job_data.get("title", "")} position at {job_data.get("company", "")}.

Job: {job_data.get("description", "")[:1500]}

Include behavioral and technical questions. Return JSON array:
["Question 1?", "Question 2?", ...]"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return get_default_questions(num)


def get_default_questions(num):
    questions = [
        "Tell me about yourself.",
        "Why are you interested in this position?",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Describe a challenging project you worked on.",
        "How do you handle conflict with teammates?",
        "What are your salary expectations?",
        "Do you have any questions for us?",
    ]
    return questions[:num]


def chat_with_ai(prompt_text, context=None):
    if not client:
        return "AI not configured. Add GEMINI_API_KEY to .env file."

    try:
        if context:
            prompt_text = f"Context: {context}\n\nQuestion: {prompt_text}"

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt_text
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error chatting with AI: {e}")
        return f"Error: {str(e)}"
