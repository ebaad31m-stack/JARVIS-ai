from core.ai_engine import ask_ai
from core.settings_agent import handle_settings_command
from core.commands import execute_command

from core.command_manager import (
    command_exists,
    list_commands,
    run_command,
)

from core.macro_manager import (
    list_macros,
    macro_exists,
    run_macro,
)

from core.memory_manager import (
    recall,
    remember,
)

from core.overlay_manager import (
    clear_overlay,
    highlight_center,
    show_overlay_message,
)

from core.responses import get_response


def process(
    command
):
    # =========================================================
    # VALIDATION
    # =========================================================

    if not command:
        return None

    command = (
        str(command)
        .lower()
        .strip()
    )

    if not command:
        return None

    # =========================================================
    # WINDOWS SETTINGS AGENT
    # =========================================================
    #
    # This runs early so simple settings commands execute
    # immediately instead of waiting for the AI.
    #
    # Examples:
    #
    # "set my wallpaper to mountains"
    # "switch windows to dark mode"
    # "turn transparency off"
    # "open bluetooth settings"
    #
    # =========================================================

    settings_response = handle_settings_command(
        command
    )

    if settings_response is not None:
        return settings_response

    # =========================================================
    # MEMORY
    # =========================================================

    if command.startswith(
        "my name is"
    ):
        name = command[
            10:
        ].strip()

        if not name:
            return (
                "You didn't tell me your name."
            )

        remember(
            "name",
            name,
        )

        return (
            f"I'll remember that your name is {name}."
        )

    if command in (
        "what is my name",
        "what's my name",
        "do you remember my name",
    ):
        name = recall(
            "name"
        )

        if name:
            return (
                f"Your name is {name}."
            )

        return (
            "I don't know your name yet."
        )

    # =========================================================
    # SCREEN OVERLAY
    # =========================================================

    if command in (
        "show overlay",
        "show the overlay",
        "test overlay",
        "test the overlay",
    ):
        show_overlay_message(
            "JARVIS screen overlay active.",
            5000,
        )

        return (
            "Overlay active."
        )

    if command in (
        "highlight center",
        "highlight the center",
        "highlight middle",
        "highlight the middle",
    ):
        highlight_center(
            "Look here",
            5000,
        )

        return (
            "Highlighting the center "
            "of your screen."
        )

    if command in (
        "clear overlay",
        "clear the overlay",
        "remove overlay",
        "hide overlay",
    ):
        clear_overlay()

        return (
            "Overlay cleared."
        )

    # =========================================================
    # LIST MACROS
    # =========================================================

    if command in (
        "list macros",
        "show macros",
        "what macros do i have",
    ):
        macros = list_macros()

        if not macros:
            return (
                "You don't have any macros configured."
            )

        return (
            "Your macros are: "
            + ", ".join(
                macros
            )
            + "."
        )

    # =========================================================
    # LIST CUSTOM COMMANDS
    # =========================================================

    if command in (
        "list custom commands",
        "show custom commands",
        "what custom commands do i have",
        "what commands did i create",
    ):
        commands = list_commands()

        if not commands:
            return (
                "You don't have any "
                "custom commands configured."
            )

        return (
            "Your custom commands are: "
            + ", ".join(
                commands
            )
            + "."
        )

    # =========================================================
    # MACROS
    # =========================================================

    macro_name = command

    macro_prefixes = (
        "run ",
        "activate ",
        "start ",
    )

    for prefix in macro_prefixes:

        if macro_name.startswith(
            prefix
        ):
            possible_name = macro_name[
                len(prefix):
            ].strip()

            if macro_exists(
                possible_name
            ):
                macro_name = possible_name
                break

    if macro_exists(
        macro_name
    ):
        result = run_macro(
            macro_name
        )

        if result:
            return (
                f"Activating {macro_name}."
            )

        return (
            f"I found {macro_name}, "
            "but one or more actions could not run."
        )

    # =========================================================
    # CUSTOM COMMANDS
    # =========================================================

    custom_name = command

    custom_prefixes = (
        "run command ",
        "activate command ",
        "execute command ",
    )

    for prefix in custom_prefixes:

        if custom_name.startswith(
            prefix
        ):
            possible_name = custom_name[
                len(prefix):
            ].strip()

            if command_exists(
                possible_name
            ):
                custom_name = possible_name
                break

    if command_exists(
        custom_name
    ):
        return run_command(
            custom_name
        )

    # =========================================================
    # NORMAL FAST COMMANDS
    # =========================================================
    #
    # App opening, closing, system commands, etc.
    # should still happen before asking the AI.
    #
    # =========================================================

    response = execute_command(
        command
    )

    if response:
        return response

    # =========================================================
    # PERSONALITY RESPONSES
    # =========================================================

    response = get_response(
        command
    )

    if response:
        return response

    # =========================================================
    # AI FALLBACK
    # =========================================================
    #
    # Only requests that weren't handled by one of JARVIS's
    # fast tools reach the AI.
    #
    # =========================================================

    return ask_ai(
        command
    )