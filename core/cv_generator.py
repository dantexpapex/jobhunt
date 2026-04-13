from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from fpdf import FPDF
import os
import logging

logger = logging.getLogger(__name__)


class CVGenerator:
    def __init__(self, output_dir="data/cvs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_cv(self, base_content, job_data, output_name=None):
        keywords = extract_keywords(job_data.get("description", ""))
        tailored_content = tailor_cv(base_content, keywords, job_data)
        file_path = self.save_cv_pdf(
            tailored_content, output_name or job_data.get("company", "generic")
        )
        return {
            "file_path": file_path,
            "keywords": ",".join(keywords),
            "content": tailored_content,
        }

    def save_cv_pdf(self, content, filename):
        pdf = ATSPDF()
        pdf.add_page()
        pdf.render_content(content)
        file_path = os.path.join(
            self.output_dir, f"{filename.lower().replace(' ', '_')}.pdf"
        )
        pdf.output(file_path)
        return file_path

    def generate_base_cv(self, personal_info, experience, skills, education):
        content = {
            "personal_info": personal_info,
            "summary": generate_summary(personal_info, experience),
            "experience": experience,
            "skills": skills,
            "education": education,
        }
        return self.save_cv_pdf(content, "base_cv")


class ATSPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Resume", 0, 1, "C")
        self.ln(5)

    def render_content(self, content):
        if "personal_info" in content:
            self.set_font("Arial", "B", 12)
            info = content["personal_info"]
            self.cell(
                0,
                10,
                f"{info.get('name', '')} - {info.get('email', '')} - {info.get('phone', '')}",
                0,
                1,
                "C",
            )
            self.ln(5)

        if "summary" in content:
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, "Professional Summary", 0, 1)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 6, content["summary"])
            self.ln(5)

        if "experience" in content:
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, "Experience", 0, 1)
            self.set_font("Arial", "", 10)
            for exp in content["experience"]:
                self.set_font("Arial", "B", 10)
                self.cell(
                    0, 6, f"{exp.get('title', '')} at {exp.get('company', '')}", 0, 1
                )
                self.set_font("Arial", "I", 9)
                self.cell(
                    0,
                    6,
                    f"{exp.get('start_date', '')} - {exp.get('end_date', '')}",
                    0,
                    1,
                )
                self.set_font("Arial", "", 10)
                self.multi_cell(0, 6, exp.get("description", ""))
                self.ln(3)
            self.ln(5)

        if "skills" in content:
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, "Skills", 0, 1)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 6, ", ".join(content["skills"]))
            self.ln(5)

        if "education" in content:
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, "Education", 0, 1)
            self.set_font("Arial", "", 10)
            for edu in content["education"]:
                self.cell(
                    0,
                    6,
                    f"{edu.get('degree', '')} - {edu.get('school', '')} ({edu.get('year', '')})",
                    0,
                    1,
                )
            self.ln(5)


def extract_keywords(job_description):
    if not job_description:
        return []

    tech_keywords = [
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "rust",
        "ruby",
        "php",
        "swift",
        "kotlin",
        "scala",
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
        "jenkins",
        "git",
        "linux",
        "react",
        "angular",
        "vue",
        "node",
        "django",
        "flask",
        "fastapi",
        "spring",
        "machine learning",
        "deep learning",
        "ai",
        "data science",
        "nlp",
        "computer vision",
        "agile",
        "scrum",
        "rest",
        "graphql",
        "microservices",
        "api",
    ]

    found = []
    desc_lower = job_description.lower()
    for kw in tech_keywords:
        if kw in desc_lower:
            found.append(kw)

    return found[:20]


def tailor_cv(base_content, keywords, job_data):
    tailored = base_content.copy()

    if "skills" in tailored and keywords:
        existing_skills = tailored.get("skills", [])
        new_skills = [kw for kw in keywords if kw not in existing_skills]
        tailored["skills"] = existing_skills + new_skills

    return tailored


def generate_summary(personal_info, experience):
    name = personal_info.get("name", "")
    years_exp = sum(exp.get("years", 0) for exp in experience)

    return f"Experienced software engineer with {years_exp}+ years of experience in developing scalable applications. Skilled in modern technologies and best practices."


def create_sample_base_cv():
    return {
        "personal_info": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "phone": "+1 234 567 8900",
            "location": "City, Country",
        },
        "summary": "Experienced software engineer...",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Company Name",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": "Developed and maintained...",
                "years": 4,
            }
        ],
        "skills": ["Python", "JavaScript", "SQL", "AWS", "Docker"],
        "education": [
            {
                "degree": "BS Computer Science",
                "school": "University Name",
                "year": "2020",
            }
        ],
    }
