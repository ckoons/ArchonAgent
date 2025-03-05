# Archon Test Search Agent

This repository contains a search agent created using Archon, an AI agent builder framework. The agent can search websites (defaulting to Google if none specified) and retrieve information based on user queries. If no query is provided, it calculates and returns the current Julian date.

## Features

- Website searching (with real Wikipedia API integration)
- Julian date calculation
- Error handling and helpful feedback
- Multiple implementation options

## Files

- `claude_test_agent.py` - Simplified agent with hardcoded examples (no input required)
- `claude_simple_agent.py` - Interactive agent without external dependencies
- `claude_agent.py` - Advanced agent using Pydantic AI (requires additional setup)
- `claude_agent_tools.py` - Tool implementations for searching and Julian date calculation
- `claude_agent_prompts.py` - System prompts for LLM integration
- `.env` and `.env.example` - Environment variable configuration
- `requirements.txt` - Dependencies for the full implementation

## Usage

### Running the Test Agent

The test agent runs with hardcoded examples and doesn't require any input:

```bash
python claude_test_agent.py
```

This will demonstrate:
1. Searching for "climate change" on Wikipedia
2. Calculating today's Julian date

### Running the Simple Agent

The simple agent is interactive and doesn't require external dependencies:

```bash
python claude_simple_agent.py
```

### Running the Full Agent

The full agent requires Pydantic AI and other dependencies:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables (copy `.env.example` to `.env` and edit)

3. Run the agent:
   ```bash
   python claude_agent.py
   ```

## Implementation Details

This agent was created using Archon, an AI agent builder framework. It demonstrates integration with both standard Python libraries and the Pydantic AI framework.

The agent provides multiple implementation options with varying levels of complexity:

1. **Basic** - Simple implementation with no dependencies
2. **Advanced** - Full-featured implementation with Pydantic AI

## Created With

- Archon
- Claude
- Pydantic AI
- Python standard libraries