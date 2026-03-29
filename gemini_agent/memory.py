"""
MemoryManager — Manages conversation history for the agent.

Stores messages in the Gemini Content format so they can be
passed directly to the model for contextual conversations.
"""

from google.generativeai.types import content_types


class MemoryManager:
    """Stores and manages conversation history within a session.

    Maintains an ordered list of messages (user, model, and function
    responses) that provides the LLM with conversational context.
    """

    def __init__(self) -> None:
        self._history: list[content_types.ContentType] = []

    def add_message(self, role: str, parts: list) -> None:
        """Append a message to the conversation history.

        Args:
            role: The message role — 'user', 'model', or 'function'.
            parts: The message parts (text, function calls, etc.).
        """
        self._history.append({"role": role, "parts": parts})

    def get_history(self) -> list[content_types.ContentType]:
        """Return the full conversation history.

        Returns:
            A list of Content-compatible dicts.
        """
        return list(self._history)

    def clear(self) -> None:
        """Clear all conversation history."""
        self._history.clear()

    @property
    def length(self) -> int:
        """Return the number of messages in history."""
        return len(self._history)
