"""Weather tool — fetches current weather using the free wttr.in API."""

from typing import Any

import requests

from gemini_agent.base_tool import BaseTool


class WeatherTool(BaseTool):
    """Fetches current weather information for a given city.

    Uses the free wttr.in service — no API key required.
    """

    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "Gets the current weather for a specified city."

    def get_declaration(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to get weather for, e.g. 'Baku' or 'London'."
                    }
                },
                "required": ["city"]
            }
        }

    def execute(self, **kwargs: Any) -> str:
        city: str = kwargs.get("city", "")
        if not city:
            return "Error: No city provided."

        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            current = data["current_condition"][0]

            weather_desc = current["weatherDesc"][0]["value"]
            temp_c = current["temp_C"]
            feels_like = current["FeelsLikeC"]
            humidity = current["humidity"]
            wind_speed = current["windspeedKmph"]

            return (
                f"Weather in {city}: {weather_desc}, "
                f"Temperature: {temp_c}°C (feels like {feels_like}°C), "
                f"Humidity: {humidity}%, Wind: {wind_speed} km/h"
            )
        except requests.exceptions.Timeout:
            return f"Error: Request timed out while fetching weather for '{city}'."
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather for '{city}': {e}"
        except (KeyError, IndexError):
            return f"Error: Could not parse weather data for '{city}'. The city may not exist."
