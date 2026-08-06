import requests

from core.personality import JARVIS_PERSONALITY
from core.config_manager import ConfigManager

config = ConfigManager()

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ai(prompt):

    model = config.get("ollama", {}).get("model", "llama3.1")
    temperature = config.get("ollama", {}).get("temperature", 0.7)

    full_prompt = f"""
{JARVIS_PERSONALITY}

User:
{prompt}

JARVIS:
"""

    data = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result.get("response", "").strip()

    except requests.exceptions.RequestException as error:
        return f"I couldn't reach my AI engine. ({error})"

    except Exception as error:
        return f"An unexpected AI error occurred: {error}"