from __future__ import annotations

from core.action_manager import (
    create_action,
    set_suggestions,
)

from core.commands import execute_command

from core.macro_manager import (
    macro_exists,
    run_macro,
)


def _command_action(
    label: str,
    command: str,
    description: str = "",
):
    return create_action(
        label=label,
        description=description,
        callback=lambda: (
            execute_command(command)
            or f"Done. {label}."
        ),
    )


def _macro_action(
    label: str,
    macro_name: str,
    description: str = "",
):
    return create_action(
        label=label,
        description=description,
        callback=lambda: (
            f"Activating {macro_name}."
            if run_macro(macro_name)
            else f"I couldn't run {macro_name}."
        ),
    )


def generate_suggestions(
    command: str,
    response: str = "",
) -> list[dict]:

    text = (
        f"{command} {response}"
        .lower()
        .strip()
    )

    actions = []

    # =====================================================
    # BORED / ENTERTAINMENT
    # =====================================================

    if any(
        phrase in text
        for phrase in (
            "i'm bored",
            "im bored",
            "i am bored",
            "something to do",
            "what should i do",
        )
    ):
        actions.append(
            _command_action(
                "Open FC 26",
                "open fc 26",
                "Launch FC 26",
            )
        )

        actions.append(
            _command_action(
                "Open YouTube",
                "open youtube",
                "Watch something",
            )
        )

        actions.append(
            _command_action(
                "Open Spotify",
                "open spotify",
                "Play some music",
            )
        )

    # =====================================================
    # GAMING
    # =====================================================

    elif any(
        phrase in text
        for phrase in (
            "gaming",
            "play a game",
            "play fc",
            "fc 26",
            "game time",
        )
    ):
        if macro_exists(
            "gaming mode"
        ):
            actions.append(
                _macro_action(
                    "Gaming Mode",
                    "gaming mode",
                    "Prepare your PC for gaming",
                )
            )

        actions.append(
            _command_action(
                "Open FC 26",
                "open fc 26",
                "Launch FC 26",
            )
        )

    # =====================================================
    # SCREEN HELP
    # =====================================================

    elif any(
        phrase in text
        for phrase in (
            "screen",
            "error",
            "what do i click",
            "what should i click",
            "look at this",
        )
    ):
        actions.append(
            _command_action(
                "Look At Screen",
                "look at my screen",
                "Let JARVIS inspect your screen",
            )
        )

        actions.append(
            _command_action(
                "Read Screen",
                "read my screen",
                "Read visible text on your screen",
            )
        )

    # =====================================================
    # PERFORMANCE
    # =====================================================

    elif any(
        word in text
        for word in (
            "cpu",
            "gpu",
            "ram",
            "performance",
            "system usage",
            "pc stats",
        )
    ):
        actions.append(
            _command_action(
                "System Report",
                "system report",
                "Check PC information",
            )
        )

    # =====================================================
    # WALLPAPER
    # =====================================================

    elif any(
        word in text
        for word in (
            "wallpaper",
            "background",
        )
    ):
        actions.append(
            _command_action(
                "Nature Wallpaper",
                "set my wallpaper to nature",
                "Try a nature wallpaper",
            )
        )

        actions.append(
            _command_action(
                "Car Wallpaper",
                "set my wallpaper to cars",
                "Try a car wallpaper",
            )
        )

        actions.append(
            _command_action(
                "Mountain Wallpaper",
                "set my wallpaper to mountains",
                "Try a mountain wallpaper",
            )
        )

    # =====================================================
    # MUSIC
    # =====================================================

    elif any(
        word in text
        for word in (
            "music",
            "spotify",
            "song",
        )
    ):
        actions.append(
            _command_action(
                "Open Spotify",
                "open spotify",
                "Open Spotify",
            )
        )

    # =====================================================
    # SAVE ACTIVE SUGGESTIONS
    # =====================================================

    set_suggestions(
        actions
    )

    return [
        {
            "id": action.action_id,
            "label": action.label,
            "description": action.description,
            "requires_confirmation":
                action.requires_confirmation,
        }
        for action in actions
    ]