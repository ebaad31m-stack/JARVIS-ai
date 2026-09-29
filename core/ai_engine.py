import requests

from core.ai_mode import (
    get_ai_mode,
    get_current_model,
    get_temperature
)

from core.conversation_manager import (
    add_turn,
    build_context
)

from core.memory_manager import (
    get_memory_context
)

from core.personality import (
    get_current_personality,
    get_personality_display_name
)


OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

AI_TIMEOUT = 180


def _build_mode_instruction(
    mode
):
    if mode == "think":

        return """
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

    return """
You are currently operating in NORMAL MODE.

Prioritize:
- fast responses
- concise answers
- natural conversation
- direct answers
- useful context from the conversation

Only expand when necessary.
"""


def _build_prompt(
    prompt,
    personality,
    mode_instruction,
    conversation_context,
    memory_context
):
    sections = []

    sections.append(
        personality
    )

    sections.append(
        mode_instruction
    )

    if memory_context:

        sections.append(
            memory_context
        )

    if conversation_context:

        sections.append(
            conversation_context
        )

    sections.append(
        "CURRENT USER MESSAGE:"
    )

    sections.append(
        str(prompt).strip()
    )

    sections.append(
        "JARVIS:"
    )

    return "\n\n".join(
        sections
    )


def ask_ai(
    prompt,
    include_history=True,
    record_conversation=False,
    source="pc"
):
    prompt = str(
        prompt or ""
    ).strip()

    if not prompt:
        return ""

    model = get_current_model()
    mode = get_ai_mode()
    temperature = get_temperature()

    personality = (
        get_current_personality()
    )

    personality_name = (
        get_personality_display_name()
    )

    mode_instruction = (
        _build_mode_instruction(
            mode
        )
    )

    conversation_context = ""

    if include_history:

        conversation_context = (
            build_context(
                limit=8,
                max_chars=12000
            )
        )

    memory_context = (
        get_memory_context()
    )

    full_prompt = _build_prompt(
        prompt=prompt,
        personality=personality,
        mode_instruction=mode_instruction,
        conversation_context=conversation_context,
        memory_context=memory_context
    )

    data = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
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

    try:

        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=AI_TIMEOUT
        )

        response.raise_for_status()

        result = response.json()

        answer = (
            result
            .get(
                "response",
                ""
            )
            .strip()
        )

        if (
            answer
            and record_conversation
        ):
            add_turn(
                user_message=prompt,
                assistant_message=answer,
                source=source
            )

        return answer

    except requests.exceptions.Timeout:

        return (
            "The AI engine took too long "
            "to respond."
        )

    except requests.exceptions.ConnectionError:

        return (
            "I couldn't reach my AI engine. "
            "Make sure Ollama is running."
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