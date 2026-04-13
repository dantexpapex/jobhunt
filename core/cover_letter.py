import google.generativeai as genai
from config import Config
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


def generate_cover_letter(job_data, personal_info):
    if not Config.GEMINI_API_KEY:
        return get_default_cover_letter(job_data, personal_info)

    prompt = build_cover_letter_prompt(job_data, personal_info)

    try:
        response = model.generate_content(prompt)
        return parse_cover_letter_response(response.text)
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return get_default_cover_letter(job_data, personal_info)


def build_cover_letter_prompt(job_data, personal_info):
    return f"""Generate a professional cover letter for a job application.

JOB POSTING:
- Title: {job_data.get("title", "")}
- Company: {job_data.get("company", "")}
- Location: {job_data.get("location", "")}
- Description: {job_data.get("description", "")[:1500]}

CANDIDATE INFO:
- Name: {personal_info.get("name", "")}
- Email: {personal_info.get("email", "")}
- Phone: {personal_info.get("phone", "")}
- Experience: {personal_info.get("experience_summary", "")}

Write a compelling cover letter (300-400 words) that:
1. Grabs attention in the first paragraph
2. Shows understanding of the company and role
3. Highlights relevant experience and skills
4. Ends with a call to action

Return ONLY the cover letter text (no JSON, no explanations)."""


def parse_cover_letter_response(response_text):
    return response_text.strip()


def get_default_cover_letter(job_data, personal_info):
    name = personal_info.get("name", "Candidate")
    company = job_data.get("company", "the company")
    title = job_data.get("title", "the position")

    return f"""Dear Hiring Manager at {company},

I am writing to express my strong interest in the {title} position at {company}. With my proven track record in software development and passion for building innovative solutions, I am confident that I would be a valuable addition to your team.

Throughout my career, I have demonstrated the ability to deliver high-quality projects while collaborating effectively with cross-functional teams. My technical skills, combined with my commitment to continuous learning, make me well-suited for this role.

I am excited about the opportunity to contribute to {company}'s mission and growth. I would welcome the chance to discuss how my background and skills align with your needs.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{name}"""


def generate_cover_letter_for_job(job_id):
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
        "location": job.location,
        "description": job.description,
    }

    return generate_cover_letter(job_data, personal_info)


def save_cover_letter(cover_letter_text, company, job_title):
    import os
    from datetime import datetime

    folder = "data/cvs"
    os.makedirs(folder, exist_ok=True)

    filename = f"cover_letter_{company.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)

    return filepath
