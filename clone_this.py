import os
import subprocess
from datetime import datetime

# Get absolute path to the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
projects_folder = os.path.join(script_dir, 'projects')
log_file = os.path.join(script_dir, 'repo_clone_log.txt')

# Ensure the projects folder exists
os.makedirs(projects_folder, exist_ok=True)

# Read the list of GitHub repo URLs
clone_list_file = os.path.join(script_dir, 'git_repo_to_clone.txt')
try:
    with open(clone_list_file, 'r') as file:
        repo_urls = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: File '{clone_list_file}' not found.")
    exit(1)

# Helper function to write log
def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as log:
        log.write(f"[{timestamp}] {message}\n")

# Process each repo URL
for url in repo_urls:
    repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(projects_folder, repo_name)

    if os.path.exists(repo_path):
        try:
            print(f"[UPDATE] Pulling updates for {repo_name}...")
            subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
            print(f"[SUCCESS] Updated {repo_name}")
            write_log(f"UPDATED: {repo_name} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to update {repo_name}: {e}")
            write_log(f"FAILED TO UPDATE: {repo_name} - {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error updating {repo_name}: {e}")
            write_log(f"ERROR UPDATING: {repo_name} - {e}")
    else:
        try:
            print(f"[CLONE] Cloning {repo_name}...")
            subprocess.run(['git', 'clone', url, repo_path], check=True)
            print(f"[SUCCESS] Cloned {repo_name}")
            write_log(f"CLONED: {repo_name} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to clone {repo_name}: {e}")
            write_log(f"FAILED TO CLONE: {repo_name} - {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error cloning {repo_name}: {e}")
            write_log(f"ERROR CLONING: {repo_name} - {e}")
