import json
import requests
import sys

def extract_owner_repo(url):
    try:
        parts = url.rstrip('/').split('/')
        return parts[-2], parts[-1]
    except Exception:
        return None, None

def check_github_branch_exists(owner, repo, branch):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    try:
        response = requests.get(api_url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def validate_plugins(file_path):
    try:
        with open(file_path, 'r') as file:
            plugins = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading plugins.json: {e}")
        sys.exit(1)

    valid_plugins = []
    broken_plugins = []

    for key, plugin in plugins.items():
        url = plugin.get('repository')
        branches = plugin.get('branch', [])

        if not url or not url.startswith(("http://", "https://")):
            print(f"❌ Invalid or missing URL for plugin '{key}': {url}")
            broken_plugins.append((key, url, "Invalid URL"))
            continue

        if not isinstance(branches, list) or not all(isinstance(b, str) for b in branches):
            print(f"❌ Invalid branch list for plugin '{key}': {branches}")
            broken_plugins.append((key, url, "Invalid branch format"))
            continue

        # Check repository accessibility
        try:
            repo_response = requests.get(url, timeout=10)
            if repo_response.status_code != 200:
                print(f"❌ Broken repo URL: {url} (HTTP {repo_response.status_code})")
                broken_plugins.append((key, url, "Repo not reachable"))
                continue
        except requests.RequestException as e:
            print(f"❌ Repo URL exception for {key}: {url} - {e}")
            broken_plugins.append((key, url, f"Request error: {e}"))
            continue

        # Check each branch
        owner, repo = extract_owner_repo(url)
        if not owner or not repo:
            print(f"❌ Could not extract owner/repo from URL: {url}")
            broken_plugins.append((key, url, "Invalid GitHub URL format"))
            continue

        all_branches_valid = True
        for branch in branches:
            if check_github_branch_exists(owner, repo, branch):
                print(f"✅ Branch '{branch}' exists for plugin '{key}'")
            else:
                print(f"❌ Branch '{branch}' does NOT exist for plugin '{key}'")
                broken_plugins.append((key, f"{url}/tree/{branch}", f"Missing branch: {branch}"))
                all_branches_valid = False

        if all_branches_valid:
            valid_plugins.append(key)

    print("\n🔍 Validation Summary:")
    print(f"✔️  Valid plugins: {len(valid_plugins)}")
    print(f"❌ Plugins with issues: {len(broken_plugins)}")

    if broken_plugins:
        print("\n❗ Issues found:")
        for item in broken_plugins:
            print(f"  - Plugin: {item[0]} | URL: {item[1]} | Reason: {item[2]}")
        sys.exit(1)

if __name__ == "__main__":
    validate_plugins('plugins.json')
