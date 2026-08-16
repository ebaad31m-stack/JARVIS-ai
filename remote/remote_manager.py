import threading


REMOTE_COMMAND_LOCK = (
    threading.Lock()
)


MAX_COMMAND_LENGTH = 2000


# =========================================================
# AI MODE PHRASES
# =========================================================

NORMAL_MODE_COMMANDS = {
    "normal mode",
    "jarvis normal mode",
    "switch to normal mode",
    "use normal mode",
}


THINK_MODE_COMMANDS = {
    "think mode",
    "thinking mode",
    "jarvis think mode",
    "jarvis thinking mode",
    "switch to think mode",
    "switch to thinking mode",
    "use think mode",
}


# =========================================================
# BLOCK HIGH-RISK REMOTE COMMANDS FOR VERSION 1
# =========================================================

BLOCKED_REMOTE_COMMANDS = {
    "exit",
    "jarvis exit",
    "shutdown jarvis",
    "shut down jarvis",

    "shutdown my computer",
    "shut down my computer",
    "shutdown the computer",
    "shut down the computer",
    "turn off my computer",
    "turn off the computer",
    "shutdown my pc",
    "shut down my pc",
    "turn off my pc",

    "confirm shutdown",
}


# =========================================================
# NORMALIZE
# =========================================================

def normalize_remote_command(
    command
):
    command = str(
        command
    ).strip()

    lowered = (
        command
        .lower()
        .strip()
    )

    prefixes = (
        "hey jarvis, ",
        "hey jarvis ",
        "jarvis, ",
        "jarvis ",
    )

    for prefix in prefixes:
        if lowered.startswith(
            prefix
        ):
            command = command[
                len(
                    prefix
                ):
            ].strip()

            break

    return command


# =========================================================
# DESKTOP AGENT
# =========================================================

def handle_remote_agent_request(
    request
):
    from core.ai_engine import (
        ask_ai,
    )

    from core.coding_agent import (
        create_project_from_response,
    )

    from core.desktop_agent import (
        paste_text,
    )

    if not isinstance(
        request,
        dict,
    ):
        return None

    kind = request.get(
        "kind"
    )

    # =====================================================
    # MESSAGE
    # =====================================================

    if kind == "message":
        return str(
            request.get(
                "message",
                "I couldn't complete that request.",
            )
        )

    # =====================================================
    # LITERAL PASTE
    # =====================================================

    if kind == "literal_paste":
        text = str(
            request.get(
                "text",
                "",
            )
        )

        if not text:
            return (
                "There was no text to type."
            )

        if paste_text(
            text
        ):
            return (
                "Done, sir."
            )

        return (
            "I couldn't type into "
            "the active window."
        )

    # =====================================================
    # AI AGENT TYPES
    # =====================================================

    if kind not in {
        "paste_ai",
        "speak_ai",
        "project",
    }:
        return None

    prompt = str(
        request.get(
            "prompt",
            "",
        )
    ).strip()

    if not prompt:
        return (
            "The request didn't contain "
            "an AI prompt."
        )

    generated = ask_ai(
        prompt
    )

    if not generated:
        return (
            "I couldn't generate "
            "the requested content."
        )

    # =====================================================
    # RETURN AI TEXT TO PHONE
    # =====================================================

    if kind == "speak_ai":
        return str(
            generated
        )

    # =====================================================
    # PASTE INTO PC
    # =====================================================

    if kind == "paste_ai":
        if paste_text(
            generated
        ):
            return str(
                request.get(
                    "success_message",
                    "Done, sir.",
                )
            )

        return (
            "I generated the content, "
            "but I couldn't paste it "
            "into the active PC window."
        )

    # =====================================================
    # PROJECT
    # =====================================================

    success, message = (
        create_project_from_response(
            generated
        )
    )

    return str(
        message
    )


# =========================================================
# EXECUTE REMOTE COMMAND
# =========================================================

def execute_remote_command(
    raw_command
):
    command = (
        normalize_remote_command(
            raw_command
        )
    )

    if not command:
        return (
            "Enter a command first."
        )

    if len(
        command
    ) > MAX_COMMAND_LENGTH:
        return (
            "That command is too long."
        )

    lowered = (
        command
        .lower()
        .strip()
    )

    # Only process one phone command at a time.
    with REMOTE_COMMAND_LOCK:

        # =====================================================
        # HIGH-RISK COMMANDS
        # =====================================================

        if lowered in BLOCKED_REMOTE_COMMANDS:
            return (
                "Remote PC shutdown and JARVIS exit "
                "are disabled in this version for safety."
            )

        # =====================================================
        # AI MODE
        # =====================================================

        if lowered in NORMAL_MODE_COMMANDS:
            from core.ai_mode import (
                get_ai_mode,
                set_ai_mode,
            )

            if (
                get_ai_mode()
                == "normal"
            ):
                return (
                    "Normal mode is already active."
                )

            set_ai_mode(
                "normal"
            )

            return (
                "Normal mode activated."
            )

        if lowered in THINK_MODE_COMMANDS:
            from core.ai_mode import (
                get_ai_mode,
                set_ai_mode,
            )

            if (
                get_ai_mode()
                == "think"
            ):
                return (
                    "Think mode is already active."
                )

            set_ai_mode(
                "think"
            )

            return (
                "Think mode activated."
            )

        # =====================================================
        # DESKTOP AGENT
        # =====================================================

        try:
            from core.agent_router import (
                build_agent_request,
            )

            agent_request = (
                build_agent_request(
                    command
                )
            )

            if agent_request is not None:
                agent_response = (
                    handle_remote_agent_request(
                        agent_request
                    )
                )

                if agent_response is not None:
                    return agent_response

        except Exception as error:
            print(
                "Remote desktop-agent error:",
                error,
            )

        # =====================================================
        # NORMAL JARVIS ROUTER
        # =====================================================

        try:
            from core.intent_router import (
                process,
            )

            response = process(
                lowered
            )

            if response is None:
                return (
                    "Command completed."
                )

            return str(
                response
            )

        except Exception as error:
            print(
                "Remote command error:",
                repr(
                    error
                ),
            )

            return (
                "JARVIS encountered an error "
                "while processing the remote command."
            )