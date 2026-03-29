"""
Main — CLI entry point for the Gemini Personal Assistant Agent.

Sets up all components (registry, memory, observer, agent),
registers tools, and runs the interactive conversation loop.
"""

import os
import sys

import google.generativeai as genai

from gemini_agent.agent import Agent
from gemini_agent.memory import MemoryManager
from gemini_agent.registry import ToolRegistry
from gemini_agent.observer import EventManager, create_logger

# Import all tools
from gemini_agent.tools.calculator import CalculatorTool
from gemini_agent.tools.weather import WeatherTool
from gemini_agent.tools.time_tool import TimeTool
from gemini_agent.tools.translator import TranslatorTool
from gemini_agent.tools.file_reader import FileReaderTool


def setup_api() -> None:
    """Configure the Gemini API key from environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Set it with: set GEMINI_API_KEY=your_api_key (Windows)")
        print("         or: export GEMINI_API_KEY=your_api_key (Linux/macOS)")
        sys.exit(1)
    genai.configure(api_key=api_key)


def create_registry() -> ToolRegistry:
    """Create a ToolRegistry and register all available tools."""
    registry = ToolRegistry()

    # Register tools — adding a new tool only requires one line here
    registry.register(CalculatorTool())
    registry.register(WeatherTool())
    registry.register(TimeTool())
    registry.register(TranslatorTool())
    registry.register(FileReaderTool())

    return registry


def create_event_manager() -> EventManager:
    """Create an EventManager and subscribe the default logger."""
    event_manager = EventManager()
    logger = create_logger()

    # Subscribe the logger to all event types
    event_manager.subscribe("tool_called", logger)
    event_manager.subscribe("tool_result", logger)
    event_manager.subscribe("error", logger)

    return event_manager


def main() -> None:
    """Run the interactive CLI agent loop."""
    print("=" * 60)
    print("  Gemini Personal Assistant Agent")
    print("  Type 'quit' or 'exit' to end the conversation.")
    print("  Type 'clear' to reset conversation history.")
    print("=" * 60)
    print()

    # --- Setup components ---
    setup_api()
    registry = create_registry()
    memory = MemoryManager()
    event_manager = create_event_manager()

    print(f"Registered tools: {', '.join(registry.tool_names)}")
    print()

    # --- Create the Agent ---
    agent = Agent(
        registry=registry,
        memory=memory,
        event_manager=event_manager,
    )

    # --- Interactive loop ---
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            memory.clear()
            print("Conversation history cleared.\n")
            continue

        # Run the agent and print the response
        response = agent.run(user_input)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
