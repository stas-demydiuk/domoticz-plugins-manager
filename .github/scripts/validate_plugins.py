import json
import requests
import sys
import time
from typing import Optional

MAX_RETRIES = 5
BASE_BACKOFF = 1  # seconds

def extract_owner_repo_branch(url: str, default_branch: Optional[str] = None):
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
    elif url.startswith("http://github.com/"):
        path = url[len("http://github.com/"):]
    else:
        return None, None, None
    
    parts = path.split('/')
    if len(parts) < 2:
        return None, None, None
    
    owner = parts[0]
    repo = parts[1]
    branch = default_branch
    
    if len(parts) >= 4 and parts[2] == 'tree':
        branch = parts[3]
    
    if repo.endswith('.git'):
        repo = repo[:-4]

    return owner, repo, branch

def request_with_retries(url: str, timeout=10):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 403:
                if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_seconds = max(reset_time - int(time.time()), 1)
                    print(f"⚠️ Rate limit hit. Sleeping for {wait_seconds} seconds before retrying...")
                    time.sleep(wait_seconds)
                    continue
                else:
                    print(f"⚠️ Forbidden (403) response for URL: {url}")
                    return response
            return response
        except requests.exceptions.RequestException as e:
            backoff = BASE_BACKOFF * (2 ** (attempt - 1))
            print(f"⚠️ Request error on attempt {attempt} for {url}: {e}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
    print(f"❌ Failed to get a successful response from {url} after {MAX_RETRIES} attempts.")
    return None

def check_url_exists(url: str) -> bool:
    response = request_with_retries(url)
    return response is not None and response.status_code == 200

def check_branch_exists(owner: str, repo: str, branch: str) -> bool:
    if not branch:
        return False
    api_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    response = request_with_retries(api_url)
    if response is None:
        return False
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        print(f"⚠️ Unexpected status {response.status_code} for branch check URL: {api_url}")
        return False

def validate_plugins(file_path: str):
    try:
        with open(file_path, 'r') as file:
            plugins = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    valid_plugins = []
    broken_urls = []
    missing_branches = []
    invalid_branch_format = []

    for key, plugin in plugins.items():
        url = plugin.get('repository')
        branch_field = plugin.get('branch')  # Optional override; can be string or list

        if not url or not url.startswith(("http://", "https://")):
            print(f"Invalid or missing URL for plugin '{key}': {url}")
            broken_urls.append((key, url))
            continue

        owner, repo, branch_from_url = extract_owner_repo_branch(url)
        if owner is None or repo is None:
            print(f"Invalid GitHub URL format for plugin '{key}': {url}")
            broken_urls.append((key, url))
            continue

        repo_url = f"https://github.com/{owner}/{repo}"
        if not check_url_exists(repo_url):
            print(f"Broken repository URL: {repo_url}")
            broken_urls.append((key, repo_url))
            continue

        # Determine branches to check (normalize to list)
        branches_to_check = None
        if branch_field:
            if isinstance(branch_field, list):
                branches_to_check = branch_field
            elif isinstance(branch_field, str):
                branches_to_check = [branch_field]
            else:
                print(f"❌ Invalid branch value for plugin '{key}': {branch_field}")
                invalid_branch_format.append((key, branch_field))
                continue
        else:
            if branch_from_url:
                branches_to_check = [branch_from_url]
            else:
                branches_to_check = ['master']

        # Check all branches exist
        all_branches_valid = True
        for branch in branches_to_check:
            if not check_branch_exists(owner, repo, branch):
                print(f"❌ Branch '{branch}' does NOT exist for plugin '{key}' at URL: {repo_url}/tree/{branch}")
                missing_branches.append((key, branch, f"{repo_url}/tree/{branch}"))
                all_branches_valid = False
        if all_branches_valid:
            print(f"✔️ Plugin '{key}' repository and branch(es) {branches_to_check} validated successfully.")
            valid_plugins.append(key)

    print("\n🔍 Validation Summary:")
    print(f"✔️  Valid plugins: {len(valid_plugins)}")
    print(f"❌ Plugins with broken URLs: {len(broken_urls)}")
    print(f"❌ Plugins with missing branches: {len(missing_branches)}")
    print(f"❌ Plugins with invalid branch format: {len(invalid_branch_format)}")

    if broken_urls or missing_branches or invalid_branch_format:
        print("❗ Issues found:")
        for key, url in broken_urls:
            print(f"  - Broken URL for plugin '{key}': {url}")
        for key, branch, checked_url in missing_branches:
            print(f"  - Missing branch '{branch}' for plugin '{key}' at URL: {checked_url}")
        for key, branch in invalid_branch_format:
            print(f"  - Invalid branch format for plugin '{key}': {branch}")
        sys.exit(1)

if __name__ == "__main__":
    validate_plugins('plugins.json')
