import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import (
    analyze_job_with_ai,
    extract_ats_keywords,
    compare_with_profile,
)

print("=" * 50)
print("Testing AI Engine")
print("=" * 50)

job_example = {
    "title": "Python Developer",
    "company": "TechCorp",
    "location": "Remote",
    "description": """
We are looking for a Python Developer with:
- 3+ years experience in Python, Django, Flask
- PostgreSQL, MongoDB databases
- REST API development
- AWS or Azure cloud experience
- Docker and Kubernetes
- Agile/Scrum methodologies
- Excellent communication skills
    """,
}

print("\n1. Analyzing job with AI...")
analysis = analyze_job_with_ai(job_example)
if analysis:
    print(f"   Score: {analysis.get('score')}/100")
    print(f"   Match: {analysis.get('match_percentage')}%")
    print(f"   Remote: {analysis.get('remote_type')}")
    print(f"   Experience: {analysis.get('experience_level')}")
    print(f"   Keywords: {analysis.get('ats_keywords', [])[:8]}")
else:
    print("   AI not available (need API key)")

print("\n2. Extracting ATS keywords...")
keywords = extract_ats_keywords(job_example["description"])
print(f"   Found {len(keywords)} keywords")
for kw in keywords[:5]:
    print(f"   - {kw}")

print("\n3. Testing profile comparison...")
cv_content = "Python developer with Django, SQL, AWS experience. Team player."
match = compare_with_profile(job_example, cv_content)
print(f"   Match Score: {match.get('match_score')}%")
print(f"   Matching: {match.get('matching_skills', [])[:5]}")
print(f"   Gaps: {match.get('gap_skills', [])[:5]}")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)
