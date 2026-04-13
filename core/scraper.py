import requests
from bs4 import BeautifulSoup
from config import Config
import logging
import re
import time

logger = logging.getLogger(__name__)

PORTAL_JOBS_API = {
    "linkedin": "https://api.linkedin.com/v2/jobs",
    "indeed": "https://indeed.com/api",
}

REMOTE_PORTALS = ["remoteok", "weworkremotely", "angellist", "hackernews"]


def search_jobs(keywords=None, locations=None, portals=None, num_jobs=50):
    if keywords is None:
        keywords = Config.SEARCH_KEYWORDS
    if locations is None:
        locations = Config.SEARCH_LOCATIONS
    if portals is None:
        portals = Config.SEARCH_PORTALS

    jobs_list = []

    for keyword in keywords:
        for location in locations:
            for portal in portals:
                try:
                    if portal == "linkedin":
                        jobs_list.extend(scrape_linkedin(keyword, location, num_jobs))
                    elif portal == "indeed":
                        jobs_list.extend(scrape_indeed(keyword, location, num_jobs))
                    elif portal == "glassdoor":
                        jobs_list.extend(scrape_glassdoor(keyword, location, num_jobs))
                except Exception as e:
                    logger.error(f"Error searching {portal}: {e}")

    return jobs_list


def search_remote_jobs(keywords=None, num_jobs=50):
    if keywords is None:
        keywords = Config.SEARCH_KEYWORDS

    jobs_list = []

    for keyword in keywords:
        jobs_list.extend(scrape_remote_ok(keyword, num_jobs))
        jobs_list.extend(scrape_weworkremotely(keyword, num_jobs))
        jobs_list.extend(scrape_hackernews(keyword, num_jobs))
        jobs_list.extend(scrape_angellist(keyword, num_jobs))

    return jobs_list


def scrape_remote_ok(keyword, num_jobs=50):
    url = f"https://remoteok.com/api?search={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data[:num_jobs]:
            if isinstance(item, dict) and item.get("position"):
                jobs.append(
                    {
                        "site": "remoteok",
                        "id": item.get("id", ""),
                        "title": item.get("position", ""),
                        "company": item.get("company", ""),
                        "location": item.get("location", "Remote"),
                        "description": item.get("description", ""),
                        "url": f"https://remoteok.com/jobs/{item.get('id', '')}",
                        "salary": item.get("salary", ""),
                        "tags": item.get("tags", []),
                    }
                )

        logger.info(f"Found {len(jobs)} jobs from RemoteOK")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping RemoteOK: {e}")
        return []


def scrape_weworkremotely(keyword, num_jobs=50):
    url = f"https://weworkremotely.com/api/jobs?search={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data.get("jobs", [])[:num_jobs]:
            jobs.append(
                {
                    "site": "weworkremotely",
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("name", ""),
                    "location": "Remote",
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "salary": item.get("salary_max", ""),
                }
            )

        logger.info(f"Found {len(jobs)} jobs from WeWorkRemotely")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping WeWorkRemotely: {e}")
        return []


def scrape_hackernews(keyword, num_jobs=50):
    url = "https://hacker-news.firebaseio.com/v0/jobstories.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        job_ids = response.json()[: num_jobs * 2]
        jobs = []

        for job_id in job_ids[:num_jobs]:
            job_url = f"https://hacker-news.firebaseio.com/v0/item/{job_id}.json"
            job_response = requests.get(job_url, headers=headers, timeout=10)

            if job_response.status_code == 200:
                item = job_response.json()
                if item and item.get("type") == "job":
                    title = item.get("title", "")
                    if keyword.lower() in title.lower():
                        jobs.append(
                            {
                                "site": "hackernews",
                                "id": str(job_id),
                                "title": title,
                                "company": item.get("by", "Unknown"),
                                "location": "Remote",
                                "description": item.get("text", ""),
                                "url": item.get("url", ""),
                            }
                        )

            time.sleep(0.5)

        logger.info(f"Found {len(jobs)} jobs from HackerNews")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping HackerNews: {e}")
        return []


def scrape_angellist(keyword, num_jobs=50):
    url = "https://api.angel.co/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data.get("jobs", [])[:num_jobs]:
            title = item.get("title", "")
            if keyword.lower() in title.lower():
                jobs.append(
                    {
                        "site": "angellist",
                        "id": str(item.get("id", "")),
                        "title": title,
                        "company": item.get("startup", {}).get("name", ""),
                        "location": item.get("location", {}).get("name", "Remote"),
                        "description": item.get("description", ""),
                        "url": item.get("angellist_url", ""),
                    }
                )

        logger.info(f"Found {len(jobs)} jobs from AngelList")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping AngelList: {e}")
        return []


def scrape_indeed(keyword, location, num_jobs=50):
    url = "https://indeed.indeed.com/api/v2/jobs"
    params = {
        "keyword": keyword,
        "location": location,
        "limit": num_jobs,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data.get("results", []):
            jobs.append(
                {
                    "site": "indeed",
                    "id": item.get("key", ""),
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("name", ""),
                    "location": item.get("location", {}).get("name", ""),
                    "description": item.get("description", {}).get("snippet", ""),
                    "url": item.get("absolute_url", ""),
                    "salary": item.get("compensation", {}).get("salary", ""),
                }
            )

        logger.info(f"Found {len(jobs)} jobs from Indeed API")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping Indeed: {e}")
        return []


def scrape_linkedin(keyword, location, num_jobs=50):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location={location}&count={num_jobs}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data.get("elements", []) if isinstance(data, dict) else data:
            job_data = (
                item.get("jobDetailsSummary", {}) if isinstance(item, dict) else {}
            )
            jobs.append(
                {
                    "site": "linkedin",
                    "id": job_data.get("jobId", ""),
                    "title": job_data.get("jobName", ""),
                    "company": job_data.get("companyName", ""),
                    "location": job_data.get("location", {}).get("location", "")
                    if isinstance(job_data.get("location"), dict)
                    else location,
                    "description": job_data.get("jobDescription", ""),
                    "url": f"https://www.linkedin.com/jobs/view/{job_data.get('jobId', '')}",
                    "salary": job_data.get("salary", {}).get("salary")
                    if isinstance(job_data.get("salary"), dict)
                    else "",
                }
            )

        logger.info(f"Found {len(jobs)} jobs from LinkedIn")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping LinkedIn: {e}")
        return []


def scrape_glassdoor(keyword, location, num_jobs=50):
    url = f"https://www.glassdoor.com/graph"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    query = {
        "query": f"""
        {{
            jobSearch(query: "{{keyword}}", location: "{{location}}", numJobs: {num_jobs}) {{
                jobs {{ id, title, company {{ name }}, location, description, indeedUrl }}
            }}
        }}
        """
    }

    try:
        response = requests.post(url, json=query, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for item in data.get("data", {}).get("jobSearch", {}).get("jobs", []):
            jobs.append(
                {
                    "site": "glassdoor",
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("name", ""),
                    "location": item.get("location", ""),
                    "description": item.get("description", ""),
                    "url": item.get("indeedUrl", ""),
                }
            )

        logger.info(f"Found {len(jobs)} jobs from Glassdoor")
        return jobs

    except Exception as e:
        logger.error(f"Error scraping Glassdoor: {e}")
        return []


def get_job_details(url, portal):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        if "linkedin" in portal.lower():
            return response.text

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()

    except Exception as e:
        logger.error(f"Error getting job details: {e}")
        return None


def format_job_data(raw_job):
    return {
        "external_id": f"{raw_job.get('site', 'unknown')}_{raw_job.get('id', '')}",
        "title": raw_job.get("title", ""),
        "company": raw_job.get("company", ""),
        "location": raw_job.get("location", ""),
        "description": raw_job.get("description", ""),
        "url": raw_job.get("url", ""),
        "portal": raw_job.get("site", ""),
        "salary_min": extract_salary(raw_job.get("salary")),
        "salary_max": extract_salary(raw_job.get("salary"), max=True),
        "salary_currency": "USD",
        "remote_type": determine_remote_type(raw_job.get("description", "")),
    }


def extract_salary(salary_str, max=False):
    if not salary_str:
        return None

    numbers = re.findall(r"\d+", str(salary_str))
    if numbers:
        if max and len(numbers) > 1:
            return int(numbers[-1])
        return int(numbers[0])
    return None


def determine_remote_type(description):
    desc_lower = description.lower() if description else ""
    if "remote" in desc_lower:
        return "remote"
    elif "hybrid" in desc_lower:
        return "hybrid"
    elif "on-site" in desc_lower or "onsite" in desc_lower or "in-person" in desc_lower:
        return "onsite"
    return "unknown"
