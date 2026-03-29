# Gemini AI Agent - Personal Assistant

An adaptive AI agent built with Python and the Google Gemini API. This CLI application functions as a digital personal assistant that maintains conversation context, analyzes user requests, and autonomously decides when to use external tools through Function Calling.

## Architecture

The system is designed using SOLID principles and GoF design patterns:

- **Strategy Pattern** — `BaseTool` abstract class defines an interchangeable tool interface
- **Factory/Registry Pattern** — `ToolRegistry` dynamically maps tool names to implementations (no if-else chains)
- **Observer Pattern** — `EventManager` provides pub/sub event logging decoupled from the agent

### ReAct Agent Loop (Reason → Act → Observe)

```
User Input → Gemini Reasons → Calls Tool (if needed) → Observes Result → Reasons Again → Final Answer
```

### Project Structure

```
gemini_agent/
├── __init__.py          # Package init
├── main.py              # CLI entry point
├── agent.py             # Agent class — ReAct loop orchestration
├── memory.py            # MemoryManager — conversation history
├── registry.py          # ToolRegistry — Factory/Registry pattern
├── base_tool.py         # BaseTool — abstract tool interface (Strategy pattern)
├── observer.py          # EventManager — Observer pattern for logging
└── tools/
    ├── __init__.py
    ├── calculator.py    # Evaluates math expressions
    ├── weather.py       # Fetches weather via wttr.in API
    ├── time_tool.py     # Returns current time for any timezone
    ├── translator.py    # Translates text via MyMemory API (Custom)
    └── file_reader.py   # Reads local file contents (Custom)
```

## Setup

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
pip install -r requirements.txt
```

### Set API Key

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Linux / macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Run

```bash
python -m gemini_agent.main
```

## Tools

| Tool | Description | Type |
|------|-------------|------|
| `calculator` | Evaluates mathematical expressions safely | Example |
| `get_weather` | Fetches current weather for a city (wttr.in) | Example |
| `get_time` | Returns current date/time for a timezone | Example |
| `translate` | Translates text between languages (MyMemory API) | Custom |
| `read_file` | Reads contents of a local text file | Custom |

## Usage Examples

```
You: What is 145 * 37 + 12?
  [tool_call] Calling tool: calculator({'expression': '145 * 37 + 12'})
  [tool_result] Tool 'calculator' returned: Result: 5377