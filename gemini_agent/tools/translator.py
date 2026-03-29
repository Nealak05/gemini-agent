"""Translator tool — translates text between languages using MyMemory API."""

from typing import Any

import requests

from gemini_agent.base_tool import BaseTool


class TranslatorTool(BaseTool):
    """Translates text from one language to another.

    Uses the free MyMemory Translation API — no API key required.
    """

    @property
    def name(self) -> str:
        return "translate"

    @property
    def description(self) -> str:
        return "Translates text from one language to another."

    def get_declaration(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to translate."
                    },
                    "source_language": {
                        "type": "string",
                        "description": "Source language code, e.g. 'en' for English, 'es' for Spanish, 'fr' for French."
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language code, e.g. 'fr' for French, 'de' for German, 'az' for Azerbaijani."
                    }
                },
                "required": ["text", "source_language", "target_language"]
            }
        }

    def execute(self, **kwargs: Any) -> str:
        text: str = kwargs.get("text", "")
        source: str = kwargs.get("source_language", "en")
        target: str = kwargs.get("target_language", "")

        if not text:
            return "Error: No text provided for translation."
        if not target:
            return "Error: No target language provided."

        try:
            lang_pair = f"{source}|{target}"
            url = "https://api.mymemory.translated.net/get"
            params = {"q": text, "langpair": lang_pair}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data["responseStatus"] == 200:
                translated = data["responseData"]["translatedText"]
                return f"Translation ({source} → {target}): {translated}"
            else:
                return f"Error: Translation failed — {data.get('responseDetails', 'Unknown error')}"
        except requests.exceptions.Timeout:
            return "Error: Translation request timed out."
        except requests.exceptions.RequestException as e:
            return f"Error during translation: {e}"
        except (KeyError, ValueError):
            return "Error: Could not parse translation response."
