import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

ATS_FORBIDDEN_WORDS = [
    "photo",
    "picture",
    "image",
    "graphic",
    "logo",
    "icon",
    "cover letter",
    "resume photo",
    "selfie",
    "linkedin url",
    "facebook",
    "instagram",
    "twitter handle",
    "salary expectation",
    "desired salary",
    "notice period",
]

ATS_SKILL_CATEGORIES = {
    "programming": [
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
        "perl",
        "r",
        "html",
        "css",
        "sql",
        "bash",
        "shell",
        "powershell",
    ],
    "frameworks": [
        "react",
        "angular",
        "vue",
        "django",
        "flask",
        "fastapi",
        "spring",
        "node.js",
        "express",
        "next.js",
        "nestjs",
        "laravel",
        "rails",
    ],
    "databases": [
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "elasticsearch",
        "oracle",
        "sql server",
        "dynamodb",
        "firebase",
        "supabase",
    ],
    "cloud": [
        "aws",
        "azure",
        "gcp",
        "ec2",
        "s3",
        "lambda",
        "rds",
        "cloudfront",
        "azure vm",
        "gcp cloud",
        "kubernetes",
        "terraform",
        "cloudformation",
    ],
    "devops": [
        "docker",
        "kubernetes",
        "jenkins",
        "ci/cd",
        "github actions",
        "gitlab",
        "jira",
        "ansible",
        "terraform",
        "puppet",
    ],
    "ai_ml": [
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "nlp",
        "chatgpt",
        "llm",
        "artificial intelligence",
        "data science",
        "pandas",
        "numpy",
        "scikit-learn",
    ],
    "soft_skills": [
        "communication",
        "teamwork",
        "leadership",
        "problem solving",
        "agile",
        "scrum",
        "project management",
        "time management",
    ],
}


def extract_ats_keywords(job_description):
    if not job_description:
        return []

    text = job_description.lower()
    found_keywords = []

    for category, skills in ATS_SKILL_CATEGORIES.items():
        for skill in skills:
            if skill.lower() in text:
                found_keywords.append(
                    {
                        "keyword": skill,
                        "category": category,
                        "count": text.count(skill.lower()),
                    }
                )

    found_keywords.sort(key=lambda x: x["count"], reverse=True)

    unique_keywords = []
    seen = set()
    for kw in found_keywords:
        if kw["keyword"] not in seen:
            unique_keywords.append(kw)
            seen.add(kw["keyword"])

    return unique_keywords


def calculate_keyword_density(keywords, cv_text):
    if not keywords or not cv_text:
        return {}

    text_lower = cv_text.lower()
    total = len(text_lower.split())
    densities = {}

    for kw in keywords:
        word = kw["keyword"].lower()
        count = text_lower.count(word)
        density = (count / total) * 100 if total > 0 else 0
        densities[word] = {
            "count": count,
            "density": round(density, 2),
            "optimal": 0.5 <= density <= 3.0,
        }

    return densities


def optimize_for_ats(cv_text, job_description):
    keywords = extract_ats_keywords(job_description)

    if not keywords:
        return {
            "optimized_cv": cv_text,
            "keywords_added": [],
            "score": 50,
            "tips": ["No keywords found to optimize"],
        }

    optimized = cv_text
    keywords_added = []

    keyword_text = ", ".join([kw["keyword"] for kw in keywords[:20]])

    sections = {
        "technical skills": None,
        "skills": None,
        "technologies": None,
        "tech stack": None,
    }

    text_lower = optimized.lower()
    has_skill_section = False

    for section in sections.keys():
        if section in text_lower:
            has_skill_section = True
            break

    if not has_skill_section:
        optimized += f"\n\nTECHNICAL SKILLS\n{keyword_text}\n"
        keywords_added = [kw["keyword"] for kw in keywords]
    else:
        for kw in keywords[:10]:
            if kw["keyword"].lower() not in text_lower:
                optimized = re.sub(
                    r"(skills|technologies|technical skills)",
                    rf"\1, {kw['keyword']}",
                    optimized,
                    flags=re.IGNORECASE,
                )
                keywords_added.append(kw["keyword"])

    score = calculate_ats_score(optimized, keywords)

    tips = generate_ats_tips(optimized, keywords)

    return {
        "optimized_cv": optimized,
        "keywords_added": keywords_added,
        "score": score,
        "tips": tips,
        "keyword_count": len(keywords),
    }


def calculate_ats_score(cv_text, keywords):
    score = 50

    if not cv_text or not keywords:
        return score

    text_lower = cv_text.lower()

    keyword_count = sum(1 for kw in keywords if kw["keyword"].lower() in text_lower)
    keyword_ratio = keyword_count / len(keywords) * 100 if keywords else 0

    score += keyword_ratio * 0.3

    if len(text_lower) > 500:
        score += 10
    if len(text_lower) < 3000:
        score += 5

    has_email = "@" in cv_text and ".com" in cv_text
    has_phone = any(c.isdigit() for c in cv_text)

    if has_email:
        score += 5
    if has_phone:
        score += 5

    return min(100, max(0, int(score)))


def generate_ats_tips(cv_text, keywords):
    tips = []

    text_lower = cv_text.lower()

    missing_keywords = [
        kw["keyword"] for kw in keywords if kw["keyword"].lower() not in text_lower
    ]

    if missing_keywords:
        tips.append(f"Add these keywords: {', '.join(missing_keywords[:5])}")

    if len(cv_text) > 3000:
        tips.append("CV is too long. Keep it under 2 pages")

    if "http" not in text_lower and "www" not in text_lower:
        tips.append("Add LinkedIn or portfolio URL")

    for word in ATS_FORBIDDEN_WORDS:
        if word in text_lower:
            tips.append(f"Remove: {word}")

    if " Duties:" in cv_text or " responsibilities:" in cv_text.lower():
        tips.append("Use action verbs instead of 'Duties' or 'Responsibilities'")

    numeric_logros = re.findall(r"\d+[+%]*", cv_text)
    if numeric_logros:
        tips.append(f"Good: Found {len(numeric_logros)} quantifiable achievements")

    return tips


def clean_for_ats(text):
    clean = text

    ascii_only = ""
    for char in clean:
        if ord(char) < 128:
            ascii_only += char
        else:
            ascii_only += " "

    clean = re.sub(r"\s+", " ", ascii_only)
    clean = clean.strip()

    lines = clean.split("\n")
    clean_lines = [line.strip() for line in lines if line.strip()]
    clean = "\n".join(clean_lines)

    return clean


def generate_ats_cv(cv_data, job_description):
    """Generate ATS-optimized CV"""
    keywords = extract_ats_keywords(job_description)

    sections = []

    if cv_data.get("name"):
        sections.append(cv_data["name"].upper())

    if cv_data.get("contact"):
        sections.append(cv_data["contact"])

    if cv_data.get("summary"):
        sections.append(f"\nPROFESSIONAL SUMMARY\n{cv_data['summary']}")

    if cv_data.get("experience"):
        exp_text = "\nWORK EXPERIENCE\n"
        for exp in cv_data["experience"]:
            exp_text += f"\n{exp.get('title', '')} - {exp.get('company', '')}\n"
            exp_text += f"{exp.get('dates', '')}\n"

            achievements = exp.get("achievements", [])
            for achv in achievements:
                if any(char.isdigit() for char in achv):
                    exp_text += f"• {achv}\n"
                else:
                    exp_text += f"• {achv}\n"

        sections.append(exp_text)

    skill_keywords = ", ".join([kw["keyword"] for kw in keywords[:25]])
    if skill_keywords:
        sections.append(f"\nTECHNICAL SKILLS\n{skill_keywords}")

    if cv_data.get("education"):
        sections.append(f"\nEDUCATION\n{cv_data.get('education', '')}")

    ats_cv = "\n\n".join(sections)
    ats_cv = clean_for_ats(ats_cv)

    score = calculate_ats_score(ats_cv, keywords)
    tips = generate_ats_tips(ats_cv, keywords)

    return {
        "cv": ats_cv,
        "score": score,
        "tips": tips,
        "keywords": [kw["keyword"] for kw in keywords],
    }


def check_ats_compatibility(cv_text):
    issues = []

    if any(word in cv_text.lower() for word in ATS_FORBIDDEN_WORDS):
        issues.append("Contains forbidden elements (photos, graphics)")

    special_chars = set(re.findall(r"[^\x00-\x7F]", cv_text))
    if special_chars:
        issues.append(f"Contains special characters: {special_chars}")

    if len(cv_text) > 6000:
        issues.append("CV too long (over 2 pages)")

    tables = cv_text.lower().count("table")
    if tables > 0:
        issues.append("Contains tables (avoid for ATS)")

    return {"compatible": len(issues) == 0, "issues": issues}
