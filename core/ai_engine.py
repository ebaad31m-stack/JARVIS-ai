import requests

from core.personality import JARVIS_PERSONALITY

from core.ai_mode import (
    get_current_model,
    get_ai_mode,
    get_temperature
)


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ai(prompt):
    model = get_current_model()
    mode = get_ai_mode()
    temperature = get_temperature()

    if mode == "think":
        mode_instruction = """
You are currently operating in THINK MODE.

Take extra care with:
- reasoning
- programming
- troubleshooting
- planning
- technical questions
- complex explanations

Prioritize accuracy and thoughtful analysis.
"""

    else:
        mode_instruction = """
You are currently operating in NORMAL MODE.

Prioritize:
- fast responses
- concise answers
- natural conversation
- direct answers

Only expand when necessary.
"""

    full_prompt = f"""
{JARVIS_PERSONALITY}

{mode_instruction}

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

    print(
        f"AI Mode: {mode.upper()} | "
        f"Model: {model} | "
        f"Temperature: {temperature}"
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return (
            result
            .get("response", "")
            .strip()
        )

    except requests.exceptions.RequestException as error:
        return (
            "I couldn't reach my AI engine. "
            f"({error})"
        )

    except Exception as error:
        return (
            "An unexpected AI error occurred: "
            f"{error}"
        )