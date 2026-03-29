"""Time tool — returns the current date and time for a given timezone."""

from datetime import datetime, timezone, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from gemini_agent.base_tool import BaseTool


class TimeTool(BaseTool):
    """Returns the current date and time for a specified timezone."""

    @property
    def name(self) -> str:
        return "get_time"

    @property
    def description(self) -> str:
        return "Gets the current date and time for a specified timezone."

    def get_declaration(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": (
                            "The timezone name, e.g. 'Asia/Baku', 'Europe/London', "
                            "'America/New_York', 'Asia/Tokyo'. Use 'UTC' for UTC time."
                        )
                    }
                },
                "required": ["timezone"]
            }
        }

    def execute(self, **kwargs: Any) -> str:
        tz_name: str = kwargs.get("timezone", "UTC")

        try:
            tz = ZoneInfo(tz_name)
            now = datetime.now(tz)
            return (
                f"Current time in {tz_name}: "
                f"{now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
        except KeyError:
            return (
                f"Error: Unknown timezone '{tz_name}'. "
                f"Use format like 'Asia/Baku', 'Europe/London', 'America/New_York'."
            )
