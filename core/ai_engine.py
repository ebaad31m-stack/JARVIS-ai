import requests

from core.ai_mode import (
    get_ai_mode,
    get_current_model,
    get_temperature
)

from core.personality import (
    get_current_personality,
    get_personality_display_name
)


OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)


def ask_ai(
    prompt
):
    model = get_current_model()
    mode = get_ai_mode()
    temperature = get_temperature()

    personality = (
        get_current_personality()
    )

    personality_name = (
        get_personality_display_name()
    )

    # =========================================================
    # THINK MODE
    # =========================================================

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

    # =========================================================
    # NORMAL MODE
    # =========================================================

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

    # =========================================================
    # FULL PROMPT
    # =========================================================

    full_prompt = f"""
{personality}

{mode_instruction}

User:
{prompt}

JARVIS:
"""

    data = {
        "model": model,

        "prompt": full_prompt,

        "stream": False,

        # Keep the normal text model loaded for a while.
        "keep_alive": "10m",

        "options": {
            "temperature": temperature
        }
    }

    print(
        f"AI Mode: {mode.upper()} | "
        f"Model: {model} | "
        f"Personality: {personality_name} | "
        f"Temperature: {temperature}"
    )

    # =========================================================
    # REQUEST
    # =========================================================

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
            .get(
                "response",
                ""
            )
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