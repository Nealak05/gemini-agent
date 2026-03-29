"""Calculator tool — evaluates mathematical expressions safely."""

import math
from typing import Any

from gemini_agent.base_tool import BaseTool


class CalculatorTool(BaseTool):
    """Evaluates mathematical expressions.

    Uses a restricted eval with only math functions allowed,
    preventing arbitrary code execution.
    """

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluates a mathematical expression and returns the result."

    def get_declaration(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2 + 3 * 4' or 'sqrt(16)'."
                    }
                },
                "required": ["expression"]
            }
        }

    def execute(self, **kwargs: Any) -> str:
        expression: str = kwargs.get("expression", "")
        if not expression:
            return "Error: No expression provided."

        # Allow only safe math operations
        allowed_names = {
            name: getattr(math, name)
            for name in dir(math)
            if not name.startswith("_")
        }
        allowed_names["abs"] = abs
        allowed_names["round"] = round

        try:
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except ZeroDivisionError:
            return "Error: Division by zero."
        except Exception as e:
            return f"Error evaluating expression '{expression}': {e}"
