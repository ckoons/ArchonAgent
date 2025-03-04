import requests
import sys

url = "http://localhost:8100/health"
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        print(f"Service is running at {url}")
        print(f"Response: {response.json()}")
    else:
        print(f"Service returned status code {response.status_code}")
except requests.RequestException as e:
    print(f"Service is not running at {url}: {e}")
    sys.exit(1)