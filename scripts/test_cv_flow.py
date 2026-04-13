import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cv_manager import CVManager
from core.cv_adapter import adapt_cv_for_job, extract_job_keywords
from core.ai_engine import analyze_job_with_ai

print("=" * 60)
print("Dynamic CV Generator - Full Flow Test")
print("=" * 60)

# Sample job from RemoteOK
job_data = {
    "title": "Senior Python Developer",
    "company": "TechCorp Inc",
    "location": "Remote",
    "description": """
We are looking for a Senior Python Developer to join our team.

Requirements:
- 5+ years Python experience
- Django, Flask, FastAPI
- PostgreSQL, MongoDB
- AWS, Docker, Kubernetes
- REST API, GraphQL
- Agile/Scrum experience
- English fluency

Nice to have:
- Machine Learning
- ChatGPT integration
- Lead experience
    """,
}

cv_manager = CVManager()

print("\n1. ANALYZING JOB WITH AI...")
analysis = analyze_job_with_ai(job_data)
print(f"   Score: {analysis.get('score')}/100")
print(f"   Match: {analysis.get('match_percentage')}%")
print(f"   Salary: {analysis.get('salary_estimate')}")
print(f"   Level: {analysis.get('experience_level')}")
print(f"   Remote: {analysis.get('remote_type')}")

print("\n2. EXTRACTING ATS KEYWORDS...")
ats_keywords = analysis.get("ats_keywords", [])
print(f"   Found: {len(ats_keywords)} keywords")
print(f"   {ats_keywords[:10]}")

print("\n3. SELECTING BEST CV BASE...")
recommended_cv = cv_manager.get_recommended_cv(job_data["title"], remote=True)
print(f"   Selected: {recommended_cv['name']}")
print(f"   File: {recommended_cv['filename']}")

print("\n4. ADAPTING CV FOR JOB...")
adapted_path = adapt_cv_for_job(recommended_cv["path"], job_data)
print(f"   Saved: {adapted_path}")

print("\n5. APPLICATION TIPS FROM AI...")
tips = analysis.get("application_tips", [])
for tip in tips:
    print(f"   - {tip}")

print("\n6. COVER LETTER TALKING POINTS...")
points = analysis.get("cover_letter_talking_points", [])
for point in points:
    print(f"   - {point}")

print("\n" + "=" * 60)
print("CV Dynamic Generation COMPLETE!")
print("=" * 60)
print(f"\nAdapted CV ready at: {adapted_path}")
print("Next: Review in dashboard -> Approve -> Apply")
