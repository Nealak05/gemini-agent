"""FileReader tool — reads the contents of a local file."""

import os
from typing import Any

from gemini_agent.base_tool import BaseTool


class FileReaderTool(BaseTool):
    """Reads and returns the contents of a local file.

    Includes safety checks for file existence, size limits,
    and restricted paths.
    """

    MAX_FILE_SIZE = 50_000  # 50 KB limit to avoid flooding the LLM

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads the contents of a local file given its path."

    def get_declaration(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read, e.g. 'data.txt' or 'src/main.py'."
                    }
                },
                "required": ["file_path"]
            }
        }

    def execute(self, **kwargs: Any) -> str:
        file_path: str = kwargs.get("file_path", "")
        if not file_path:
            return "Error: No file path provided."

        # Resolve to absolute path
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return f"Error: File '{file_path}' does not exist."

        if not os.path.isfile(abs_path):
            return f"Error: '{file_path}' is not a file (might be a directory)."

        file_size = os.path.getsize(abs_path)
        if file_size > self.MAX_FILE_SIZE:
            return (
                f"Error: File '{file_path}' is too large "
                f"({file_size:,} bytes, limit is {self.MAX_FILE_SIZE:,} bytes)."
            )

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"Contents of '{file_path}':\n{content}"
        except UnicodeDecodeError:
            return f"Error: File '{file_path}' is not a valid text file."
        except PermissionError:
            return f"Error: Permission denied to read '{file_path}'."
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"
