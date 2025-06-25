import json
import requests
import sys

def extract_owner_repo_branch(url, default_branch=None):
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
    elif url.startswith("http://github.com/"):
        path = url[len("http://github.com/"):]
    else:
        return None, None, None
    
    parts = path.split('/')
    # Expect at least owner/repo
    if len(parts) < 2:
        return None, None, None
    
    owner = parts[0]
    repo = parts[1]
    branch = default_branch
    
    # If URL contains /tree/branch, extract branch
    if len(parts) >= 4 and parts[2] == 'tree':
        branch = parts[3]
    
    # Remove '.git' suffix if present
    if repo.endswith('.git'):
        repo = repo[:-4]

    return owner, repo, branch

def check_url_exists(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_branch_exists(owner, repo, branch):
    if not branch:
        return False
    api_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    try:
        response = requests.get(api_url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def validate_plugins(file_path):
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
        branch_field = plugin.get('branch')

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

        # Determine branches to check
        if branch_field is None:
            branch_to_check = branch_from_url if branch_from_url else 'master'
            branches_to_check = [branch_to_check]
        else:
            if isinstance(branch_field, str):
                branches_to_check = [branch_field]
            elif isinstance(branch_field, list):
                if all(isinstance(b, str) for b in branch_field):
                    branches_to_check = branch_field
                else:
                    print(f"❌ Invalid branch list for plugin '{key}': {branch_field}")
                    invalid_branch_format.append((key, branch_field))
                    continue
            else:
                print(f"❌ Invalid branch value for plugin '{key}': {branch_field}")
                invalid_branch_format.append((key, branch_field))
                continue

        # Check branches existence
        missing = []
        for branch in branches_to_check:
            if not check_branch_exists(owner, repo, branch):
                branch_url = f"https://github.com/{owner}/{repo}/tree/{branch}"
                print(f"❌ Branch '{branch}' does NOT exist for plugin '{key}' at URL: {branch_url}")
                missing.append(branch_url)

        if missing:
            missing_branches.append((key, missing))
            continue

        print(f"✔️ Plugin '{key}' repository and branch(es) {branches_to_check} validated successfully.")
        valid_plugins.append(repo_url)

    # Summary
    print("\n🔍 Validation Summary:")
    print(f"✔️  Valid plugins: {len(valid_plugins)}")
    print(f"❌ Plugins with broken URLs: {len(broken_urls)}")
    print(f"❌ Plugins with missing branches: {len(missing_branches)}")
    print(f"❌ Plugins with invalid branch format: {len(invalid_branch_format)}")

    if broken_urls or missing_branches or invalid_branch_format:
        print("❗ Issues found:")
        for key, url in broken_urls:
            print(f"  - Broken URL for plugin '{key}': {url}")
        for key, branch_urls in missing_branches:
            for branch_url in branch_urls:
                print(f"  - Missing branch URL for plugin '{key}': {branch_url}")
        for key, branch in invalid_branch_format:
            print(f"  - Invalid branch format for plugin '{key}': {branch}")
        sys.exit(1)

if __name__ == "__main__":
    validate_plugins('plugins.json')
