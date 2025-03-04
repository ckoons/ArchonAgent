#!/usr/bin/env python3
"""
ClaudeCode Use Archon Tool

This script demonstrates how Claude Code can use Archon as a tool
to generate a new AI agent based on user requirements.
"""

import requests
import time
import json
import uuid
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
STREAMLIT_URL = "http://localhost:8501"
LOG_FILE = "workbench/claudecode_archon_tool.log"

# Ensure log directory exists
os.makedirs("workbench", exist_ok=True)

def log_message(message):
    """Log a message to the log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

class ArchonTool:
    """Tool class for Claude Code to interact with Archon"""
    
    def __init__(self):
        self.verify_archon_running()
        # Initialize the driver for Streamlit interaction
        self.setup_browser()
        
    def verify_archon_running(self):
        """Verify that Archon's Streamlit UI is running"""
        try:
            response = requests.get(STREAMLIT_URL, timeout=5)
            if response.status_code != 200:
                log_message(f"❌ Archon Streamlit UI returned status code {response.status_code}")
                sys.exit(1)
            log_message("✅ Archon Streamlit UI is running")
        except requests.RequestException as e:
            log_message(f"❌ Failed to connect to Archon Streamlit UI: {str(e)}")
            sys.exit(1)
    
    def setup_browser(self):
        """Set up the browser for Streamlit interaction"""
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Initialize the Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            log_message("✅ Browser initialized for Streamlit interaction")
        except Exception as e:
            log_message(f"❌ Failed to initialize browser: {str(e)}")
            sys.exit(1)
    
    def create_agent_from_prompt(self, prompt):
        """Create an agent using Archon based on a prompt"""
        log_message(f"Creating agent from prompt: {prompt}")
        
        try:
            # Open the Archon Streamlit app
            self.driver.get(STREAMLIT_URL)
            
            # Wait for the page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            # Navigate to the Chat tab
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
            for tab in tabs:
                if "Chat" in tab.text:
                    tab.click()
                    log_message("Navigated to Chat tab")
                    break
            
            # Wait for the chat input to appear
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
            
            # Input the prompt
            textarea = self.driver.find_element(By.CSS_SELECTOR, "textarea")
            textarea.send_keys(prompt)
            
            # Submit the prompt
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[kind='primary']")
            send_button.click()
            log_message("Submitted prompt to Archon")
            
            # Wait for a response (this may need adjustment based on Archon's UI)
            time.sleep(30)  # Allow time for Archon to process and respond
            
            # Capture the response
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".stChatMessage div")
            response_text = "\n".join([elem.text for elem in response_elements if elem.text])
            
            log_message("Received response from Archon")
            
            # Extract code blocks
            code_blocks = self.extract_code_blocks(response_text)
            
            # Implement the agent code
            if code_blocks:
                self.implement_agent_code(code_blocks)
                return True, "Agent created successfully", code_blocks
            else:
                return False, "No code blocks found in Archon's response", {}
            
        except Exception as e:
            log_message(f"❌ Error creating agent: {str(e)}")
            return False, f"Error creating agent: {str(e)}", {}
        finally:
            # Clean up
            self.driver.quit()
    
    def extract_code_blocks(self, text):
        """Extract code blocks from Archon's response"""
        code_blocks = {}
        
        # Very simple extraction - in a real implementation, this would be more robust
        lines = text.split('\n')
        current_file = None
        current_content = []
        
        for line in lines:
            if line.startswith('```') and current_file is None:
                # Look for filename on the same line
                parts = line.strip('`').strip().split()
                if len(parts) > 1 and '.' in parts[1]:
                    current_file = parts[1]
                    log_message(f"Found code block for file: {current_file}")
            elif line.startswith('```') and current_file is not None:
                # End of code block
                code_blocks[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
            elif current_file is not None:
                # Content of code block
                current_content.append(line)
        
        log_message(f"Extracted {len(code_blocks)} code blocks")
        return code_blocks
    
    def implement_agent_code(self, code_blocks):
        """Implement the agent code extracted from Archon's response"""
        # Create a unique directory for the agent
        agent_dir = f"agents/archon_agent_{int(time.time())}"
        os.makedirs(agent_dir, exist_ok=True)
        log_message(f"Created directory for agent: {agent_dir}")
        
        # Write each file
        for filename, content in code_blocks.items():
            file_path = os.path.join(agent_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            log_message(f"Created file: {file_path}")
        
        return agent_dir

def main():
    """Main function to demonstrate Claude Code using Archon as a tool"""
    log_message("=== Claude Code Using Archon Tool ===")
    
    # Example user prompt
    user_prompt = "Create a news summarization agent that can fetch and summarize news articles from various sources."
    
    # Initialize the Archon tool
    archon_tool = ArchonTool()
    
    # Create an agent from the prompt
    success, message, code_blocks = archon_tool.create_agent_from_prompt(user_prompt)
    
    # Report results
    if success:
        log_message(f"✅ {message}")
        log_message(f"Created files: {list(code_blocks.keys())}")
    else:
        log_message(f"❌ {message}")
    
    log_message("=== End of Demonstration ===")

if __name__ == "__main__":
    main()