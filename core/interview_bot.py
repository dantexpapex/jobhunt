import json
import logging

logger = logging.getLogger(__name__)

try:
    from google import genai
    from config import Config

    AI_AVAILABLE = Config.GEMINI_API_KEY
    if AI_AVAILABLE:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
    else:
        client = None
except:
    client = None
    AI_AVAILABLE = False


INTERVIEW_QUESTIONS_BANK = {
    "behavioral": [
        "Tell me about yourself",
        "Why do you want to work here?",
        "What are your greatest strengths and weaknesses?",
        "Describe a challenging project you worked on",
        "How do you handle conflict with teammates?",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?",
        "Tell me about a time you failed and what you learned",
    ],
    "technical": [
        "Explain the difference between REST and GraphQL",
        "What is your tech stack and why did you choose it?",
        "How do you optimize a slow database query?",
        "Describe your experience with Agile/Scrum",
        "What's the difference between SQL and NoSQL?",
        "How would you design a system that handles 1M users?",
        "Explain CI/CD pipelines",
        "What design patterns do you use most?",
    ],
    "company_specific": [
        "What do you know about our company?",
        "Why do you want to work here specifically?",
        "How would you contribute to our team?",
        "What products of ours do you use?",
    ],
}


def generate_interview_response(question, context=None):
    if not client or not AI_AVAILABLE:
        return generate_basic_response(question)

    prompt = f"""Generate a professional interview answer.

Question: {question}
Context: {context or "software engineering role"}

Provide a 2-3 sentence answer that is:
- Concise and specific
- Uses the STAR method when applicable
- Highlights relevant experience

Return ONLY the answer text."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return generate_basic_response(question)


def generate_basic_response(question):
    question_lower = question.lower()

    responses = {
        "tell me about yourself": "I'm a software developer with experience in Python, JavaScript, and cloud technologies. I've worked on web applications and automation projects, and I'm passionate about building efficient solutions.",
        "why do you want to work here": "I'm excited about your company because of the innovative products and the opportunity to work with modern technologies. The company culture aligns with my professional goals.",
        "greatest strengths": "My greatest strengths are problem-solving, communication, and adaptability. I'm able to quickly learn new technologies and collaborate effectively with teams.",
        "challenging project": "One challenging project I worked on involved optimizing a slow database query. I analyzed the issue, implemented caching, and improved performance by 80%.",
        "where do you see yourself in 5 years": "In 5 years, I see myself as a senior developer or tech lead, contributing to architectural decisions and mentoring junior developers.",
        "why should we hire you": "You should hire me because I have the technical skills, the passion for learning, and the teamwork abilities to contribute meaningfully to your team.",
        "conflict with teammates": "When I have conflict with teammates, I focus on understanding their perspective, communicate openly, and find a compromise that works for everyone.",
    }

    for key, answer in responses.items():
        if key in question_lower:
            return answer

    return "That's a great question. I'm ready to discuss my experience and how it applies to this role."


def generate_follow_up_email(
    type, company, position, context=None, candidate_name="Candidate"
):
    templates = {
        "after_apply": f"""Subject: Follow-up on {position} Application

Dear Hiring Manager,

I recently submitted my application for the {position} position at {company}. I'm very excited about the opportunity to join your team.

I wanted to briefly highlight why I'm a strong fit:
- My technical skills align with your requirements
- I'm passionate about {context or "building great products"}
- I'd love to contribute to your team's success

Thank you for considering my application. I'm happy to provide any additional information.

Best regards
{candidate_name}
""",
        "after_interview": f"""Subject: Thank you - {position} Interview

Dear [Interviewer],

Thank you for taking the time to meet with me today about the {position} position. I enjoyed learning more about your team and the exciting work at {company}.

Our conversation reinforced my enthusiasm for the role and the company. I'm confident that my skills in {context or "software development"} would allow me to contribute meaningfully.

Please don't hesitate to reach out if you need any additional information.

Best regards
{candidate_name}
""",
        "no_response": f"""Subject: Following up - {position} Application

Dear Hiring Manager,

I hope this message finds you well. I wanted to follow up on my application for the {position} role at {company}, submitted a few weeks ago.

I'm still very interested in the opportunity and would love to discuss any updates on the hiring process. I'm available to chat at your convenience.

Thank you for your time.

Best regards
{candidate_name}
""",
        "accept_offer": f"""Subject: Excited to Accept - {position}

Dear Hiring Manager,

I'm thrilled to accept the offer for the {position} position at {company}! Thank you for this opportunity.

I'm excited to join the team on [start date] and contribute to the company's success.

Please let me know if there's anything I need to prepare before my start date.

Best regards
{candidate_name}
""",
    }

    return templates.get(type, templates["after_apply"])


def generate_interview_cheatsheet(job_description):
    key_topics = extract_topics(job_description)

    cheatsheet = {
        "topics_to_study": key_topics,
        "company_research": [],
        "questions_to_ask": [],
        "materials": [],
    }

    if "python" in job_description.lower():
        cheatsheet["topics_to_study"].extend(["Python", "Django", "FastAPI"])
    if "react" in job_description.lower():
        cheatsheet["topics_to_study"].extend(["React", "JavaScript", "TypeScript"])
    if "aws" in job_description.lower() or "cloud" in job_description.lower():
        cheatsheet["topics_to_study"].extend(["AWS", "EC2", "S3", "Lambda"])

    cheatsheet["questions_to_ask"] = [
        "What's the team structure?",
        "What are the biggest challenges facing the team?",
        "How does the company support professional development?",
        "What's the technology stack?",
        "How is the work-life balance?",
    ]

    return cheatsheet


def extract_topics(text):
    if not text:
        return []

    topics = []
    text_lower = text.lower()

    tech_topics = {
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "angular",
        "django",
        "flask",
        "node",
        "express",
        "sql",
        "postgresql",
        "mongodb",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "machine learning",
        "ai",
        "data",
        "api",
        "rest",
        "graphql",
    }

    for topic in tech_topics:
        if topic in text_lower:
            topics.append(topic.title())

    return topics[:10]
