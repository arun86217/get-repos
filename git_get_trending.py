import os
import subprocess
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://github.com"
LANGUAGE = "python"
TIME_RANGES = ["daily", "weekly", "monthly"]
CSV_FILE = "trending_repos.csv"
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projects')

# Ensure project directory exists
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Load existing repo data
repo_data = {}
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            repo_data[row["repo_url"]] = row

# Helper to write/update CSV
def update_csv():
    with open(CSV_FILE, "w", newline='') as f:
        fieldnames = ["repo_name", "repo_url", "created_at", "last_updated"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in repo_data.values():
            writer.writerow(row)

# Fetch trending repos by time range
def fetch_trending(time_range):
    url = f"https://github.com/trending/{LANGUAGE}?since={time_range}"
    print('='*15)
    print(url)
    print('='*15)
    headers = {"Accept-Language": "en-US"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    repo_links = soup.find_all("h2", class_="h3")

    repos = []
    for link in repo_links:
        relative_url = link.a['href'].strip()
        full_url = BASE_URL + relative_url
        repos.append(full_url)
    return repos

# Clone or pull a repo
def process_repo(repo_url):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_owner = repo_url.rstrip("/").split("/")[-2]
    repo_dir = os.path.join(PROJECTS_DIR, f"{repo_name}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(repo_dir):
        try:
            print(f"[PULL] {repo_name}")
            subprocess.run(["git", "-C", repo_dir, "pull"], check=True)
            repo_data[repo_url]["last_updated"] = now
        except Exception as e:
            print(f"[ERROR] Failed to pull {repo_name}: {e}")
    else:
        try:
            print(f"[CLONE] {repo_name}")
            subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
            repo_data[repo_url] = {
                "repo_name": f"{repo_owner}/{repo_name}",
                "repo_url": repo_url,
                "created_at": now,
                "last_updated": now
            }
        except Exception as e:
            print(f"[ERROR] Failed to clone {repo_name}: {e}")

# Main workflow
for time_range in TIME_RANGES:
    print(f"\n==> Fetching {time_range} trending repos...")
    trending_repos = fetch_trending(time_range)
    for repo in trending_repos:
        process_repo(repo)

# Save updates
update_csv()
print("\n✅ Done. All repos processed and CSV updated.")
