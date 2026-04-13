import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cv_manager import CVManager
from core.cv_adapter import (
    adapt_cv_for_job,
    extract_job_keywords,
    extract_missing_keywords,
)

print("=" * 50)
print("Testing CV Adapter")
print("=" * 50)

manager = CVManager()

job_example = {
    "title": "Python Developer",
    "company": "TechCorp",
    "description": """
We are looking for a Python Developer with experience in:
- Python, Django, Flask, FastAPI
- PostgreSQL, MongoDB
- AWS or Azure cloud services
- Docker and Kubernetes
- REST API development
- Machine Learning is a plus
- Remote work available
    """,
}

print("\n1. Extracting job keywords...")
keywords = extract_job_keywords(job_example["description"])
print(f"   Found keywords: {keywords}")

print("\n2. Testing CV selection...")
cv = manager.get_recommended_cv(job_example["title"])
print(f"   Selected CV: {cv['name']}")

print("\n3. Extracting CV content...")
cv_content = manager.extract_content_from_docx(cv["path"])
print(f"   CV length: {len(cv_content)} chars")

print("\n4. Finding missing keywords...")
missing = extract_missing_keywords(job_example["description"], cv_content)
print(f"   Missing keywords to add: {missing}")

print("\n5. Creating adapted CV...")
adapted_path = adapt_cv_for_job(cv["path"], job_example)
print(f"   Adapted CV saved to: {adapted_path}")

if adapted_path and os.path.exists(adapted_path):
    print(f"   [OK] File exists: {os.path.getsize(adapted_path)} bytes")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)
