# Claude Code Integration with Archon

This document provides comprehensive information on integrating Claude Code with Archon, the AI agent builder framework.

## Overview

Archon is an "Agenteer" - an AI agent designed to autonomously build, refine, and optimize other AI agents. It provides a streamlined workflow for creating Pydantic AI agents with proper tool implementation, error handling, and documentation.

The Claude Code integration allows users to:
1. Create new AI agents directly from Claude Code
2. Interact with Archon in a conversational manner
3. Automatically implement generated agent code into the workspace

## Repository Information

- Original Repository: https://github.com/coleam00/Archon.git
- Current Fork: https://github.com/ckoons/ArchonAgent.git

## Quick Start Guide

**IMPORTANT: Always start Claude in the `ArchonAgent` directory to ensure all relative paths work correctly.**

### Step 1: Start Archon Services

First, launch Archon using Docker (recommended):
```bash
# Navigate to the ArchonAgent directory
cd /Users/cskoons/projects/github/ArchonAgent

# Start Archon using Docker
python run_docker.py
```

This will start:
- Streamlit UI on port 8501 (http://localhost:8501)
- Graph Service on port 8100 (http://localhost:8100/health)

### Step 2: Complete Archon Setup (First-time Only)

If this is your first time running Archon:
1. Open http://localhost:8501 in your browser
2. Navigate to the "Intro" tab
3. Follow the guided setup process:
   - Configure environment variables (API keys, model settings)
   - Set up Supabase database connection
   - Crawl Pydantic AI documentation
   - Start the agent service

### Step 3: Verify Graph Service Connection

In a new terminal:
```bash
cd /Users/cskoons/projects/github/ArchonAgent
python check_service.py
```

You should see: `Archon Graph Service is running!`

### Step 4: Start Claude MCP Adapter

In another terminal:
```bash
cd /Users/cskoons/projects/github/ArchonAgent
python claude_integration/claude_mcp_adapter.py
```

You should see: `Claude Code MCP Adapter for Archon starting...`

### Step 5: Test the Integration

To verify everything is working:
```bash
cd /Users/cskoons/projects/github/ArchonAgent
python claude_integration/claude_archon_example.py
```

## Hybrid Agent Creation Approach

We use a hybrid approach for creating agents:

1. **Use Archon for**:
   - Initial agent structure
   - Core functionality
   - Pydantic AI best practices
   - Complex tool chains
   - RAG capabilities

2. **Use Claude for**:
   - Customizing and extending agents
   - Adapting code to specific requirements
   - Troubleshooting and debugging
   - Fine-tuning prompts and behaviors

This combines Archon's expertise in Pydantic AI patterns with Claude's ability to adapt code to your unique needs.

## Available Claude Integration Tools

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

## GitHub Workflow

When making changes to the repository:

### Regular Syncing with Original Repo
```bash
# Navigate to your repository
cd /Users/cskoons/projects/github/ArchonAgent

# Fetch updates from the original repository
git fetch origin

# Merge changes from original repository into your main branch
git merge origin/main

# If there are conflicts, resolve them manually
# Then commit the resolved conflicts:
git add .
git commit -m "Resolve merge conflicts with original repository"

# Push the merged changes to your GitHub repository
git push ckoons main
```

### Making Claude Integration Changes
```bash
# Make changes to files in the claude_integration directory
cd /Users/cskoons/projects/github/ArchonAgent/claude_integration

# Commit your changes
git add .
git commit -m "Improve Claude integration: [description of changes]"

# Push your changes
git push ckoons main
```

This workflow maintains a clean separation between the original code and your Claude integration.

## Troubleshooting

- **Connection Issues**: If the standard adapter doesn't connect, use the debug version:
  ```bash
  python claude_integration/claude_mcp_adapter_debug.py
  ```

- **Service Not Found**: If you get "Service not found" errors:
  1. Check if Docker containers are running: `docker ps`
  2. Restart Archon services: `python run_docker.py`
  3. Verify Graph Service: `curl http://localhost:8100/health`

- **Log Files**: Check logs in `workbench/claude_logs.txt` for detailed error information

- **Environment Variables**: Verify environment variables are properly set in `.env` files

## Useful Commands

- `python run_docker.py` - Start Archon in Docker containers
- `streamlit run streamlit_ui.py` - Start Archon UI locally
- `python claude_integration/claude_mcp_adapter.py` - Start the Claude Code MCP adapter
- `python check_service.py` - Check if the Archon graph service is running
- `git remote -v` - View remote repositories
- `git push ckoons main` - Push changes to your fork

## Additional Resources

- [Archon Documentation](iterations/v4-streamlit-ui-overhaul/README.md)
- [Pydantic AI Documentation](https://docs.pydantic.ai)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [MCP Documentation](https://anthropic.github.io/anthropic-tools/mcp/server/)