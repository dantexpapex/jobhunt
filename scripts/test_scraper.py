import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scraper import (
    scrape_remote_ok,
    scrape_weworkremotely,
    scrape_hackernews,
    scrape_indeed,
    scrape_linkedin,
)

print("=" * 50)
print("Testing Job Scrapers")
print("=" * 50)

print("\n1. Testing RemoteOK...")
jobs = scrape_remote_ok("python", 10)
print(f"   Found {len(jobs)} jobs")
for j in jobs[:3]:
    print(f"   - {j.get('title')} @ {j.get('company')}")

print("\n2. Testing WeWorkRemotely...")
jobs = scrape_weworkremotely("python", 10)
print(f"   Found {len(jobs)} jobs")
for j in jobs[:3]:
    print(f"   - {j.get('title')} @ {j.get('company')}")

print("\n3. Testing Indeed...")
jobs = scrape_indeed("python developer", "Remote", 10)
print(f"   Found {len(jobs)} jobs")
for j in jobs[:3]:
    print(f"   - {j.get('title')} @ {j.get('company')}")

print("\n4. Testing LinkedIn...")
jobs = scrape_linkedin("python developer", "Remote", 10)
print(f"   Found {len(jobs)} jobs")
for j in jobs[:3]:
    print(f"   - {j.get('title')} @ {j.get('company')}")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)
