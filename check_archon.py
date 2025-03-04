#!/usr/bin/env python3
"""
Script to check Archon's availability and test basic interaction
"""

import requests
import sys
import json
import os
import uuid

def check_streamlit_ui():
    """Check if Archon's Streamlit UI is accessible"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            return True, "Archon Streamlit UI is running"
        else:
            return False, f"Archon Streamlit UI returned status code {response.status_code}"
    except requests.RequestException as e:
        return False, f"Failed to connect to Archon Streamlit UI: {str(e)}"

def check_graph_service():
    """Check if Archon's Graph Service API is accessible"""
    try:
        response = requests.get("http://localhost:8100/health", timeout=5)
        if response.status_code == 200:
            return True, f"Archon Graph Service is running: {response.json()}"
        else:
            return False, f"Archon Graph Service returned status code {response.status_code}"
    except requests.RequestException as e:
        return False, f"Failed to connect to Archon Graph Service: {str(e)}"

def test_graph_service_api():
    """Test basic interaction with Archon's Graph Service API"""
    try:
        # Create a thread ID
        thread_id = str(uuid.uuid4())
        
        # Build the request payload
        payload = {
            "message": "Create a simple calculator agent that can add, subtract, multiply, and divide",
            "thread_id": thread_id,
            "is_first_message": True
        }
        
        # Send the request
        print(f"Sending test request to Archon Graph Service with thread_id: {thread_id}")
        response = requests.post("http://localhost:8100/invoke", json=payload, timeout=60)
        
        if response.status_code == 200:
            return True, f"Test request successful. Response: {response.json()}"
        else:
            return False, f"Test request failed with status code {response.status_code}"
    except requests.RequestException as e:
        return False, f"Test request failed: {str(e)}"

def main():
    """Main function to check Archon's availability"""
    print("=== Checking Archon Availability ===\n")
    
    # Check Streamlit UI
    ui_available, ui_message = check_streamlit_ui()
    print(f"Streamlit UI: {'✅' if ui_available else '❌'} {ui_message}")
    
    # Check Graph Service
    service_available, service_message = check_graph_service()
    print(f"Graph Service: {'✅' if service_available else '❌'} {service_message}")
    
    # If both are available, test the API
    if ui_available and service_available:
        print("\n=== Testing Archon Graph Service API ===\n")
        test_success, test_message = test_graph_service_api()
        print(f"API Test: {'✅' if test_success else '❌'} {test_message}")
    
    # Exit with appropriate status code
    if not (ui_available and service_available):
        print("\n⚠️ Archon is not fully accessible. Make sure both the Streamlit UI and Graph Service are running.")
        sys.exit(1)
    else:
        print("\n✅ Archon is fully accessible and ready to use.")
        sys.exit(0)

if __name__ == "__main__":
    main()