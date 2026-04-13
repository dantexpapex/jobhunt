import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.advanced_features import get_company_ranking, predict_success
from core.interview_bot import (
    generate_interview_response,
    generate_follow_up_email,
    generate_interview_cheatsheet,
)

print("=" * 60)
print("ADVANCED FEATURES TEST")
print("=" * 60)

print("\n1. COMPANY RANKING...")
rank = get_company_ranking("Google")
print(f"   Google Tier: {rank['company_tier']}")
print(f"   Score: {rank['overall_score']}")

rank = get_company_ranking("RemoteOK Startup")
print(f"   Startup Tier: {rank['company_tier']}")
print(f"   Score: {rank['overall_score']}")

print("\n2. SUCCESS PREDICTION...")
job_data = {
    "company": "TechCorp",
    "title": "Python Developer",
    "description": "Python, Django, AWS, REST API",
}
history = {"applied": 10, "interview": 2}
prediction = predict_success(job_data, history)
print(f"   Predicted Success: {prediction['predicted_success']}%")
print(f"   Recommendation: {prediction['recommendation']}")

print("\n3. INTERVIEW RESPONSE...")
response = generate_interview_response("Tell me about yourself")
print(f"   Response: {response[:100]}...")

print("\n4. FOLLOW-UP EMAIL...")
email = generate_follow_up_email("after_apply", "TechCorp", "Developer")
print(f"   Subject: Follow-up on Developer Application")

print("\n5. INTERVIEW CHEATSHEAT...")
cheatsheet = generate_interview_cheatsheet("Python Django AWS")
print(f"   Topics: {cheatsheet['topics_to_study'][:5]}")
print(f"   Questions to ask: {cheatsheet['questions_to_ask'][:3]}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
