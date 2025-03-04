import socket
import requests
from contextlib import closing

def check_port(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        return result == 0

ports = [8100, 8501]
print("Port scanning results:")
for port in ports:
    status = "OPEN" if check_port('localhost', port) else "CLOSED"
    print(f"Port {port}: {status}")

try:
    response = requests.get("http://localhost:8501", timeout=5)
    print(f"Streamlit UI is running (status code {response.status_code})")
except Exception as e:
    print(f"Streamlit UI check failed: {e}")

try:
    response = requests.get("http://localhost:8100/health", timeout=5)
    print(f"Graph service API is running (status code {response.status_code})")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Graph service API check failed: {e}")