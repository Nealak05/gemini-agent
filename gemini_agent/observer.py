"""
EventManager — Observer Pattern for monitoring agent activity.

Provides a lightweight pub/sub system so that logging, analytics,
or UI updates can react to agent events without tight coupling.
"""

from collections import defaultdict
from typing import Any, Callable


class EventManager:
    """Simple Observer (pub/sub) for agent events.

    Components publish events (e.g., 'tool_called', 'error') and
    subscribers react without the publisher knowing about them.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable[..., Any]) -> None:
        """Subscribe a callback to an event type.

        Args:
            event: The event name (e.g., 'tool_called', 'error').
            callback: A callable that receives the event data.
        """
        self._subscribers[event].append(callback)

    def publish(self, event: str, data: Any = None) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event name.
            data: Arbitrary data passed to each subscriber.
        """
        for callback in self._subscribers.get(event, []):
            try:
                callback(data)
            except Exception:
                pass  # Observers must not break the main flow


def create_logger() -> Callable:
    """Create a simple logging callback for agent events.

    Returns:
        A callback function that prints event data to the console.
    """
    def log_event(data: Any) -> None:
        if isinstance(data, dict):
            event_type = data.get("type", "event")
            message = data.get("message", str(data))
            print(f"  [{event_type}] {message}")
        else:
            print(f"  [log] {data}")

    return log_event
