"""
ToolRegistry — Factory/Registry Pattern for managing tools.

Maps tool names to their implementations using a dictionary lookup,
avoiding if-else chains. New tools are registered dynamically.
"""

from typing import Any

from gemini_agent.base_tool import BaseTool


class ToolRegistry:
    """Manages registration and execution of tools.

    Implements the Factory/Registry Pattern: tools register themselves
    by name, and the registry handles lookup and execution.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool in the registry.

        Args:
            tool: A BaseTool instance to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        """Retrieve a tool by name.

        Args:
            name: The tool name to look up.

        Returns:
            The BaseTool instance, or None if not found.
        """
        return self._tools.get(name)

    def get_all_declarations(self) -> list[dict]:
        """Return function declarations for all registered tools.

        Returns:
            A list of declaration dicts for Gemini function calling.
        """
        return [tool.get_declaration() for tool in self._tools.values()]

    def execute_tool(self, name: str, **kwargs: Any) -> str:
        """Look up a tool by name and execute it.

        Args:
            name: The tool name returned by the LLM.
            **kwargs: Arguments for the tool.

        Returns:
            The tool's string result, or an error message.
        """
        tool = self.get_tool(name)
        if tool is None:
            return f"Error: Unknown tool '{name}'. Available tools: {list(self._tools.keys())}"

        try:
            return tool.execute(**kwargs)
        except TypeError as e:
            return f"Error: Invalid arguments for tool '{name}': {e}"
        except Exception as e:
            return f"Error: Tool '{name}' failed: {e}"

    @property
    def tool_names(self) -> list[str]:
        """Return a list of all registered tool names."""
        return list(self._tools.keys())
