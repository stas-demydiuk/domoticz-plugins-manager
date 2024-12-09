import json
import requests

def validate_plugins(file_path):
    with open(file_path, 'r') as file:
        plugins = json.load(file)

    for key, plugin in plugins.items():
        url = plugin['repository']
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Valid URL: {url}")
            else:
                print(f"Broken URL: {url}")
        except requests.exceptions.RequestException as e:
            print(f"Broken URL: {url} - Exception: {e}")

if __name__ == "__main__":
    validate_plugins('plugins.json')
