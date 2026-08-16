import json
import os
import time
import webbrowser

import pyautogui

from core.app_launcher import (
    close_app,
    launch_app,
)

from core.macro_manager import (
    macro_exists,
    run_macro,
)

from core.paths import user_file

from core.vision_manager import (
    inspect_screen_question,
)


COMMANDS_FILE = user_file(
    "custom_commands.json"
)


# =========================================================
# LOAD
# =========================================================

def load_commands():
    if not os.path.exists(
        COMMANDS_FILE
    ):
        save_commands(
            {}
        )

        return {}

    try:
        with open(
            COMMANDS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        if isinstance(
            data,
            dict,
        ):
            return data

    except Exception as error:
        print(
            "Custom command load error:",
            error,
        )

    return {}


# =========================================================
# SAVE
# =========================================================

def save_commands(
    commands
):
    os.makedirs(
        os.path.dirname(
            COMMANDS_FILE
        ),
        exist_ok=True,
    )

    with open(
        COMMANDS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            commands,
            file,
            indent=4,
        )


# =========================================================
# EXISTS
# =========================================================

def command_exists(
    name
):
    name = (
        str(
            name
        )
        .lower()
        .strip()
    )

    return (
        name
        in load_commands()
    )


# =========================================================
# LIST
# =========================================================

def list_commands():
    return sorted(
        load_commands().keys()
    )


# =========================================================
# SAVE ONE COMMAND
# =========================================================

def set_command(
    name,
    actions,
):
    name = (
        str(
            name
        )
        .lower()
        .strip()
    )

    if not name:
        return False

    if not isinstance(
        actions,
        list,
    ):
        return False

    commands = load_commands()

    commands[
        name
    ] = actions

    save_commands(
        commands
    )

    return True


# =========================================================
# DELETE
# =========================================================

def delete_command(
    name
):
    name = (
        str(
            name
        )
        .lower()
        .strip()
    )

    commands = load_commands()

    if name not in commands:
        return False

    del commands[
        name
    ]

    save_commands(
        commands
    )

    return True


# =========================================================
# OPEN URL
# =========================================================

def open_url(
    target
):
    target = (
        str(
            target
        )
        .strip()
    )

    if not target:
        return False

    if not (
        target.startswith(
            "http://"
        )
        or target.startswith(
            "https://"
        )
    ):
        target = (
            "https://"
            + target
        )

    try:
        webbrowser.open(
            target
        )

        return True

    except Exception as error:
        print(
            "Custom command URL error:",
            error,
        )

        return False


# =========================================================
# HOTKEY PARSER
# =========================================================

def run_hotkey(
    target
):
    target = (
        str(
            target
        )
        .lower()
        .strip()
    )

    if not target:
        return False

    aliases = {
        "control": "ctrl",
        "escape": "esc",
        "return": "enter",
        "windows": "win",
        "window": "win",
    }

    keys = []

    for key in target.split(
        "+"
    ):
        key = key.strip()

        if not key:
            continue

        key = aliases.get(
            key,
            key,
        )

        keys.append(
            key
        )

    if not keys:
        return False

    try:
        if len(
            keys
        ) == 1:
            pyautogui.press(
                keys[0]
            )

        else:
            pyautogui.hotkey(
                *keys
            )

        return True

    except Exception as error:
        print(
            "Custom command hotkey error:",
            error,
        )

        return False


# =========================================================
# RUN SINGLE ACTION
# =========================================================

def run_action(
    action
):
    if not isinstance(
        action,
        dict,
    ):
        return {
            "success": False,
            "message": "",
        }

    action_type = (
        str(
            action.get(
                "action",
                "",
            )
        )
        .lower()
        .strip()
    )

    # =====================================================
    # OPEN APP
    # =====================================================

    if action_type == "open_app":
        target = (
            str(
                action.get(
                    "target",
                    "",
                )
            )
            .lower()
            .strip()
        )

        result = launch_app(
            target
        )

        return {
            "success":
                bool(
                    result
                ),

            "message":
                "",
        }

    # =====================================================
    # CLOSE APP
    # =====================================================

    if action_type == "close_app":
        target = (
            str(
                action.get(
                    "target",
                    "",
                )
            )
            .lower()
            .strip()
        )

        result = close_app(
            target
        )

        return {
            "success":
                bool(
                    result
                ),

            "message":
                "",
        }

    # =====================================================
    # OPEN WEBSITE
    # =====================================================

    if action_type == "open_url":
        result = open_url(
            action.get(
                "target",
                "",
            )
        )

        return {
            "success": result,
            "message": "",
        }

    # =====================================================
    # WAIT
    # =====================================================

    if action_type == "wait":
        try:
            seconds = float(
                action.get(
                    "seconds",
                    1,
                )
            )

            seconds = max(
                0,
                min(
                    seconds,
                    60,
                ),
            )

            time.sleep(
                seconds
            )

            return {
                "success": True,
                "message": "",
            }

        except Exception as error:
            print(
                "Custom command wait error:",
                error,
            )

            return {
                "success": False,
                "message": "",
            }

    # =====================================================
    # RUN MACRO
    # =====================================================

    if action_type == "run_macro":
        target = (
            str(
                action.get(
                    "target",
                    "",
                )
            )
            .lower()
            .strip()
        )

        if not macro_exists(
            target
        ):
            return {
                "success": False,
                "message": "",
            }

        result = run_macro(
            target
        )

        return {
            "success":
                bool(
                    result
                ),

            "message":
                "",
        }

    # =====================================================
    # SPEAK TEXT
    # =====================================================

    if action_type == "speak_text":
        text = (
            str(
                action.get(
                    "target",
                    "",
                )
            )
            .strip()
        )

        return {
            "success":
                bool(
                    text
                ),

            "message":
                text,
        }

    # =====================================================
    # TYPE TEXT
    # =====================================================

    if action_type == "type_text":
        text = str(
            action.get(
                "target",
                "",
            )
        )

        if not text:
            return {
                "success": False,
                "message": "",
            }

        try:
            pyautogui.write(
                text,
                interval=0.01,
            )

            return {
                "success": True,
                "message": "",
            }

        except Exception as error:
            print(
                "Custom command typing error:",
                error,
            )

            return {
                "success": False,
                "message": "",
            }

    # =====================================================
    # HOTKEY
    # =====================================================

    if action_type == "hotkey":
        result = run_hotkey(
            action.get(
                "target",
                "",
            )
        )

        return {
            "success": result,
            "message": "",
        }

    # =====================================================
    # SCREEN VISION
    # =====================================================

    if action_type == "vision":
        question = (
            str(
                action.get(
                    "target",
                    "",
                )
            )
            .strip()
        )

        if not question:
            question = (
                "Describe what is currently "
                "visible on my screen."
            )

        response = inspect_screen_question(
            question
        )

        return {
            "success":
                bool(
                    response
                ),

            "message":
                response,
        }

    print(
        "Unknown custom command action:",
        action_type,
    )

    return {
        "success": False,
        "message": "",
    }


# =========================================================
# RUN COMMAND
# =========================================================

def run_command(
    name
):
    commands = load_commands()

    name = (
        str(
            name
        )
        .lower()
        .strip()
    )

    if name not in commands:
        return None

    actions = commands[
        name
    ]

    if not isinstance(
        actions,
        list,
    ):
        return (
            f"I couldn't run {name}."
        )

    success_count = 0
    messages = []

    for action in actions:
        try:
            result = run_action(
                action
            )

            if result.get(
                "success",
                False,
            ):
                success_count += 1

            message = (
                result.get(
                    "message",
                    "",
                )
                .strip()
            )

            if message:
                messages.append(
                    message
                )

        except Exception as error:
            print(
                f"Custom command action error in '{name}':",
                error,
            )

    if messages:
        return " ".join(
            messages
        )

    if success_count > 0:
        return (
            f"{name.capitalize()} activated."
        )

    return (
        f"I found {name}, "
        "but I couldn't run its actions."
    )