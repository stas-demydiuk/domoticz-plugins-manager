import json
import requests
import sys

def validate_plugins(file_path):
    try:
        with open(file_path, 'r') as file:
            plugins = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading plugins.json: {e}")
        sys.exit(1)

    valid_urls = []
    broken_urls = []

    for key, plugin in plugins.items():
        url = plugin.get('repository')  # Use `.get()` to avoid KeyError
        if not url or not url.startswith(("http://", "https://")):
            print(f"Invalid or missing URL for plugin {key}: {url}")
            broken_urls.append((key, url))
            continue

        try:
            response = requests.get(url, timeout=10)  # Add timeout
            if response.status_code == 200:
                print(f"Valid URL: {url}")
                valid_urls.append(url)
            else:
                print(f"Broken URL: {url} (HTTP {response.status_code})")
                broken_urls.append((key, url))
        except requests.exceptions.RequestException as e:
            print(f"Broken URL: {url} - Exception: {e}")
            broken_urls.append((key, url))

    # Output summary
    print("\nValidation Summary:")
    print(f"Valid URLs: {len(valid_urls)}")
    print(f"Broken URLs: {len(broken_urls)}")

    # Exit with non-zero status code if broken URLs are found
    if broken_urls:
        sys.exit(1)

if __name__ == "__main__":
    validate_plugins('plugins.json')
