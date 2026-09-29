from __future__ import annotations

import threading

from core.action_manager import (
    get_action_state,
)

from core.agent_router import (
    build_agent_request,
)

from core.suggestion_engine import (
    generate_suggestions,
)


REMOTE_COMMAND_LOCK = threading.RLock()

MAX_COMMAND_LENGTH = 2000


NORMAL_MODE_PHRASES = {
    "normal mode",
    "switch to normal mode",
    "use normal mode",
    "normal ai mode",
}


THINK_MODE_PHRASES = {
    "think mode",
    "switch to think mode",
    "use think mode",
    "thinking mode",
}


BLOCKED_REMOTE_COMMANDS = {
    "exit",
    "quit",
    "close jarvis",
    "shutdown jarvis",
    "stop jarvis",
    "shutdown pc",
    "shut down pc",
    "shutdown computer",
    "shut down computer",
    "turn off pc",
    "turn off computer",
    "confirm shutdown",
}


def normalize_remote_command(
    command: str,
) -> str:
    text = (
        str(command)
        .strip()
    )

    lowered = (
        text
        .lower()
        .strip()
    )

    prefixes = (
        "hey jarvis,",
        "hey jarvis:",
        "hey jarvis ",
        "jarvis,",
        "jarvis:",
        "jarvis ",
    )

    for prefix in prefixes:
        if lowered.startswith(prefix):
            text = (
                text[
                    len(prefix):
                ]
                .strip()
            )
            break

    return text


def _finalize_response(
    command: str,
    response,
) -> str:
    if response is None:
        response = ""

    response_text = str(
        response
    )

    try:
        generate_suggestions(
            command,
            response_text,
        )

    except Exception as error:
        print(
            "[Remote] Suggestion generation failed:",
            error,
        )

    return response_text


def _coding_language_from_request(
    prompt: str,
) -> str:
    text = (
        str(prompt or "")
        .lower()
    )

    if (
        "typescript" in text
        or " ts " in f" {text} "
    ):
        return "typescript"

    if (
        "javascript" in text
        or "node.js" in text
        or "nodejs" in text
    ):
        return "javascript"

    if (
        "html" in text
        and "css" not in text
        and "javascript" not in text
    ):
        return "html"

    if "css" in text:
        return "css"

    if "sql" in text:
        return "sql"

    if (
        "powershell" in text
        or "power shell" in text
    ):
        return "powershell"

    return "python"


def handle_remote_agent_request(
    request: dict,
) -> str | None:

    if not request:
        return None

    # The modern agent router uses "kind".
    # Older remote code used "type".
    request_type = str(
        request.get(
            "kind",
            request.get(
                "type",
                "",
            ),
        )
    ).lower().strip()

    # =====================================================
    # SIMPLE MESSAGE
    # =====================================================

    if request_type == "message":
        message = request.get(
            "message",
            "",
        )

        if message:
            return str(
                message
            )

        return None

    # =====================================================
    # LITERAL PASTE
    # =====================================================

    if request_type == "literal_paste":
        text = str(
            request.get(
                "text",
                "",
            )
        )

        if not text:
            return "There was nothing to paste."

        try:
            from core.desktop_agent import (
                paste_text,
            )

            paste_text(
                text
            )

            return "Done. I pasted it."

        except Exception as error:
            return (
                "I couldn't paste that: "
                f"{error}"
            )

    # =====================================================
    # AI PASTE
    # =====================================================

    if request_type == "paste_ai":
        prompt = str(
            request.get(
                "prompt",
                "",
            )
        )

        if not prompt:
            return (
                "I need something to "
                "generate first."
            )

        try:
            from core.ai_engine import (
                ask_ai,
            )

            from core.desktop_agent import (
                paste_text,
            )

            result = ask_ai(
                prompt
            )

            paste_text(
                str(result)
            )

            return str(
                result
            )

        except Exception as error:
            return (
                "I couldn't generate "
                "and paste that: "
                f"{error}"
            )

    # =====================================================
    # SPEAK AI
    # =====================================================

    if request_type == "speak_ai":
        prompt = str(
            request.get(
                "prompt",
                "",
            )
        )

        if not prompt:
            return None

        try:
            from core.ai_engine import (
                ask_ai,
            )

            return str(
                ask_ai(
                    prompt
                )
            )

        except Exception as error:
            return (
                "I couldn't answer that: "
                f"{error}"
            )

    # =====================================================
    # DEDICATED CODING AGENT
    # =====================================================

    if request_type in {
        "coding_project",
        "project",
    }:
        prompt = str(
            request.get(
                "prompt",
                "",
            )
        ).strip()

        if not prompt:
            return None

        try:
            from core.coding_agent import (
                create_project_from_prompt,
            )

            result = create_project_from_prompt(
                prompt,
                open_project=True,
            )

            message = str(
                getattr(
                    result,
                    "message",
                    "Coding task completed.",
                )
            )

            if getattr(
                result,
                "success",
                False,
            ):
                return message

            return (
                "The Coding Agent finished, "
                "but it found a problem. "
                + message
            )

        except Exception as error:
            return (
                "I couldn't process that coding "
                "project: "
                f"{error}"
            )

    if request_type == "coding_script":
        prompt = str(
            request.get(
                "prompt",
                "",
            )
        ).strip()

        if not prompt:
            return None

        try:
            from core.coding_agent import (
                write_script_from_prompt,
            )

            result = write_script_from_prompt(
                prompt,
                language=_coding_language_from_request(
                    prompt
                ),
            )

            message = str(
                getattr(
                    result,
                    "message",
                    "Coding task completed.",
                )
            )

            if getattr(
                result,
                "success",
                False,
            ):
                return message

            return (
                "The Coding Agent finished, "
                "but it found a problem. "
                + message
            )

        except Exception as error:
            return (
                "I couldn't process that coding "
                "task: "
                f"{error}"
            )

    return None


def execute_remote_command(
    command: str,
) -> str:

    with REMOTE_COMMAND_LOCK:

        command = normalize_remote_command(
            command
        )

        if not command:
            return "Send me a command first."

        if len(command) > MAX_COMMAND_LENGTH:
            return "That command is too long."

        lowered = (
            command
            .lower()
            .strip()
        )

        # =================================================
        # SAFETY
        # =================================================

        if lowered in BLOCKED_REMOTE_COMMANDS:
            return (
                "That command isn't available "
                "through the remote connection."
            )

        # =================================================
        # AI MODE
        # =================================================

        if lowered in NORMAL_MODE_PHRASES:
            try:
                from core.ai_engine import (
                    set_ai_mode,
                )

                set_ai_mode(
                    "normal"
                )

                return _finalize_response(
                    command,
                    "Normal AI mode is active.",
                )

            except Exception:
                return _finalize_response(
                    command,
                    "Normal mode requested.",
                )

        if lowered in THINK_MODE_PHRASES:
            try:
                from core.ai_engine import (
                    set_ai_mode,
                )

                set_ai_mode(
                    "think"
                )

                return _finalize_response(
                    command,
                    "Think mode is active.",
                )

            except Exception:
                return _finalize_response(
                    command,
                    "Think mode requested.",
                )

        # =================================================
        # AGENT ROUTER
        # =================================================

        try:
            agent_request = build_agent_request(
                command
            )

        except Exception as error:
            print(
                "[Remote] Agent router error:",
                error,
            )

            agent_request = None

        if agent_request:
            agent_response = (
                handle_remote_agent_request(
                    agent_request
                )
            )

            if agent_response is not None:
                return _finalize_response(
                    command,
                    agent_response,
                )

        # =================================================
        # NORMAL JARVIS ROUTER
        # =================================================

        try:
            from core.intent_router import (
                process,
            )

            response = process(
                command
            )

        except Exception as error:
            return _finalize_response(
                command,
                (
                    "I couldn't run that command: "
                    f"{error}"
                ),
            )

        return _finalize_response(
            command,
            response,
        )


def get_remote_action_state() -> dict:

    try:
        return get_action_state()

    except Exception:
        return {
            "pending": None,
            "suggestions": [],
        }