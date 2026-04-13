import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.local_tracker import add_application, get_tracker_stats, get_all_tracker

print("=" * 50)
print("Testing Local Tracker")
print("=" * 50)

test_job = {
    "company": "TechCorp",
    "title": "Python Developer",
    "location": "Remote",
    "portal": "RemoteOK",
    "salary": "$80,000 - $120,000",
    "url": "https://remoteok.com/jobs/123",
}

test_app = {"status": "pending", "notes": "Test application"}

print("\n1. Adding test application...")
result = add_application(test_job, test_app)
print(f"   Success: {result}")

print("\n2. Getting stats...")
stats = get_tracker_stats()
print(f"   Stats: {stats}")

print("\n3. Getting all applications...")
apps = get_all_tracker()
print(f"   Total: {len(apps)}")
for app in apps[:3]:
    print(f"   - {app.get('Empresa')} | {app.get('Puesto')} | {app.get('Estado')}")

print("\n" + "=" * 50)
print("Tracker test complete!")
print("=" * 50)
