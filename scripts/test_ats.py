import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ats_optimizer import (
    extract_ats_keywords,
    optimize_for_ats,
    calculate_ats_score,
    generate_ats_tips,
    check_ats_compatibility,
    ATS_SKILL_CATEGORIES,
)

print("=" * 60)
print("ATS OPTIMIZER TEST")
print("=" * 60)

job_description = """
We are looking for a Python Developer with:
- 3+ years Python experience
- Django, Flask, FastAPI
- PostgreSQL, MongoDB
- AWS or Azure cloud
- Docker, Kubernetes
- REST API development
- Agile/Scrum experience
- Excellent communication skills
"""

print("\n1. EXTRACTING ATS KEYWORDS...")
keywords = extract_ats_keywords(job_description)
print(f"   Found {len(keywords)} keywords")
for kw in keywords[:10]:
    print(f"   - [{kw['category']}] {kw['keyword']}")

print("\n2. TESTING OPTIMIZATION...")
sample_cv = """
JOHN DOE
Email: john@example.com | Phone: +1 234 567 8900

PROFESSIONAL SUMMARY
Experienced Python developer with strong problem-solving skills.

WORK EXPERIENCE
Python Developer - Tech Corp - 2020-Present
- Developed web applications using Python and Django
- Managed databases with PostgreSQL
- Collaborated with team using Agile methodology

SKILLS
Python, JavaScript, HTML, CSS
"""

result = optimize_for_ats(sample_cv, job_description)
print(f"   ATS Score: {result['score']}/100")
print(f"   Keywords added: {len(result['keywords_added'])}")
print(f"   Tips:")
for tip in result["tips"][:5]:
    print(f"      - {tip}")

print("\n3. CHECKING ATS COMPATIBILITY...")
compat = check_ats_compatibility(sample_cv)
print(f"   Compatible: {compat['compatible']}")
if compat["issues"]:
    print(f"   Issues: {compat['issues']}")

print("\n4. ATS SCORE TEST...")
score = calculate_ats_score(sample_cv, keywords)
print(f"   Score: {score}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
