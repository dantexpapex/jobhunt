import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cv_manager import CVManager

print("=" * 50)
print("Testing CV Manager")
print("=" * 50)

manager = CVManager()

print(f"\nCVs available: {len(manager.available_cvs)}")
for cv in manager.available_cvs:
    print(f"  - {cv['name']}")

print("\n" + "=" * 30)
print("Testing CV selection by job title")
print("=" * 30)

test_jobs = [
    "Python Developer",
    "Web Developer",
    "Automation Specialist",
    "Junior Programmer",
    "Remote Virtual Assistant",
    "Data Analyst",
]

for job in test_jobs:
    cv = manager.get_recommended_cv(job)
    print(f"\nJob: {job}")
    print(f"  Recommended: {cv['name'] if cv else 'None'}")

print("\n" + "=" * 30)
print("Testing content extraction")
print("=" * 30)

content = manager.extract_content_from_docx(manager.available_cvs[0]["path"])
print(f"\nSample from {manager.available_cvs[0]['name']}:")
print(content[:500] if content else "No content extracted")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)
