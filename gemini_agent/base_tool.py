"""
BaseTool — Abstract base class for all agent tools.

Implements the Strategy Pattern: each tool is an interchangeable strategy
that the agent can dynamically select and execute based on LLM decisions.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract interface that all tools must implement.

    This ensures the Open/Closed Principle (OCP): new tools can be added
    by creating a new subclass without modifying the Agent or Registry.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    @abstractmethod
    def get_declaration(self) -> dict:
        """Return the function declaration schema for Gemini function calling.

        Returns:
            A dictionary matching the Gemini FunctionDeclaration format.
        """
        ...

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """Execute the tool with the given arguments.

        Args:
            **kwargs: Tool-specific arguments provided by the LLM.

        Returns:
            A string result to be fed back to the LLM.
        """
        ...
