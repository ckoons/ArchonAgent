# Claude Code Integration with Archon

This document provides information on integrating Claude Code with Archon, the AI agent builder framework.

## Overview

Archon is an "Agenteer" - an AI agent designed to autonomously build, refine, and optimize other AI agents. It provides a streamlined workflow for creating Pydantic AI agents with proper tool implementation, error handling, and documentation.

The Claude Code integration allows users to:
1. Create new AI agents directly from Claude Code
2. Interact with Archon in a conversational manner
3. Automatically implement generated agent code into the workspace

## Repository Information

- Original Repository: https://github.com/coleam00/Archon.git
- Current Fork: https://github.com/ckoons/ArchonAgent.git

## Setup Instructions

### Prerequisites
- Archon running locally (default: http://localhost:8501)
- Archon Graph Service API (default: http://localhost:8100)
- Properly configured environment (.env file with API keys)
- Python 3.11+ with required packages (pydantic-ai, mcp, etc.)

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ckoons/ArchonAgent.git
   cd ArchonAgent
   ```

2. Start Archon services:
   ```bash
   # If using Docker (recommended)
   python run_docker.py
   
   # If running locally
   streamlit run streamlit_ui.py
   ```

3. Run the setup script to verify configuration:
   ```bash
   python setup_claude_integration.py
   ```

4. Start the Claude Code MCP adapter:
   ```bash
   python claude_mcp_adapter.py
   ```

5. Use the Archon tools in Claude Code to create AI agents

## Available Tools

The integration provides the following tools to Claude Code:

- `create_archon_thread()` - Creates a new conversation thread with Archon
- `run_archon_agent(thread_id, user_input)` - Sends requests to Archon to generate agent code
- `implement_agent_code(file_path, code)` - Saves generated code to files
- `get_archon_status()` - Checks if Archon is running properly

## Usage Examples

### Creating a New Agent

```
I need a weather agent that can fetch forecast data for multiple cities
```

### Improving an Existing Agent

```
Can you add error handling to this agent for when the API is unavailable?
```

### Implementing the Generated Agent

The generated agent code will be automatically inserted into your workspace after creation. Archon generates complete agent implementations including:

- `agent.py` - Main agent definition
- `agent_tools.py` - Tool implementations
- `agent_prompts.py` - System prompts
- `.env.example` - Required environment variables
- `requirements.txt` - Dependencies

## Successfully Created Agents

### Weather Forecast Agent
- Created in `agents/weather_agent_1740989316/`
- Fetches current weather conditions and forecasts for multiple cities
- Uses WeatherAPI.com to retrieve data including:
  - Temperature, conditions, wind speed, humidity
  - Air quality information
  - Simple contextual information
- Successfully tested with Atlanta and Beijing forecasts

## Testing the Integration

You can test the integration without a full Claude Code setup:

```bash
# Run the example script to see how Claude Code would interact with Archon
python claude_archon_example.py

# Test the direct implementation of agent code
python simple_test.py

# Test the weather agent
cd agents/weather_agent_1740989316
python agent.py
```

## Troubleshooting

- If connection fails, ensure Archon is running and graph service is accessible
- Check logs in `workbench/claude_logs.txt` for detailed error information
- For debugging, use `claude_mcp_adapter_debug.py` which works even if the Archon API is unstable
- Verify environment variables are properly set in `.env` files
- If pushing changes to GitHub, ensure you're using the correct remote:
  ```bash
  # Add your fork as a remote (if not already added)
  git remote add ckoons https://github.com/ckoons/ArchonAgent.git
  
  # Push to your fork instead of the original repository
  git push ckoons main
  ```

## Useful Commands

- `python run_docker.py` - Start Archon in Docker containers
- `streamlit run streamlit_ui.py` - Start Archon UI locally
- `python claude_mcp_adapter.py` - Start the Claude Code MCP adapter
- `python check_service.py` - Check if the Archon graph service is running
- `git remote -v` - View remote repositories
- `git push ckoons main` - Push changes to your fork

## Additional Resources

- [Archon Documentation](iterations/v4-streamlit-ui-overhaul/README.md)
- [Pydantic AI Documentation](https://docs.pydantic.ai)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [MCP Documentation](https://anthropic.github.io/anthropic-tools/mcp/server/)

## Known Limitations

- The current implementation requires both Archon and Claude Code to be running on the same machine
- The MCP adapter does not yet support streaming responses from Archon
- Authentication between Claude Code and the MCP adapter is not yet implemented

## Potential Enhancements

- Add support for hourly forecasts and weather alerts to the weather agent
- Create additional agents (news summarizer, translation tool, etc.)
- Improve error handling and add streaming support to the Claude Code integration
- Test with alternative weather APIs or data sources
- Develop a more sophisticated UI for interacting with generated agents
- Create additional documentation and examples in the repository