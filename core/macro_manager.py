import json
import os
import time
import webbrowser

from core.app_launcher import (
    close_app,
    launch_app
)

from core.paths import user_file


MACROS_FILE = user_file(
    "macros.json"
)


DEFAULT_MACROS = {
    "gaming mode": [
        {
            "action": "open_app",
            "target": "discord"
        },
        {
            "action": "wait",
            "seconds": 1
        },
        {
            "action": "open_app",
            "target": "fc 26"
        }
    ]
}


# =========================================================
# LOAD MACROS
# =========================================================

def load_macros():
    if not os.path.exists(
        MACROS_FILE
    ):
        save_macros(
            DEFAULT_MACROS
        )

        return DEFAULT_MACROS.copy()

    try:
        with open(
            MACROS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(
                file
            )

        if isinstance(
            data,
            dict
        ):
            return data

    except Exception as error:
        print(
            "Macro load error:",
            error
        )

    return {}


# =========================================================
# SAVE MACROS
# =========================================================

def save_macros(
    macros
):
    os.makedirs(
        os.path.dirname(
            MACROS_FILE
        ),
        exist_ok=True
    )

    with open(
        MACROS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            macros,
            file,
            indent=4
        )


# =========================================================
# CHECK MACRO
# =========================================================

def macro_exists(
    name
):
    macros = load_macros()

    name = (
        name
        .lower()
        .strip()
    )

    return name in macros


# =========================================================
# RUN SINGLE ACTION
# =========================================================

def run_action(
    action
):
    if not isinstance(
        action,
        dict
    ):
        return False

    action_type = (
        str(
            action.get(
                "action",
                ""
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
                    ""
                )
            )
            .lower()
            .strip()
        )

        if not target:
            return False

        result = launch_app(
            target
        )

        if result is None:
            print(
                f"Macro app not found: {target}"
            )

            return False

        return bool(
            result
        )

    # =====================================================
    # CLOSE APP
    # =====================================================

    if action_type == "close_app":
        target = (
            str(
                action.get(
                    "target",
                    ""
                )
            )
            .lower()
            .strip()
        )

        if not target:
            return False

        result = close_app(
            target
        )

        return bool(
            result
        )

    # =====================================================
    # WAIT
    # =====================================================

    if action_type == "wait":
        try:
            seconds = float(
                action.get(
                    "seconds",
                    1
                )
            )

            seconds = max(
                0,
                min(
                    seconds,
                    60
                )
            )

            time.sleep(
                seconds
            )

            return True

        except Exception as error:
            print(
                "Macro wait error:",
                error
            )

            return False

    # =====================================================
    # OPEN URL
    # =====================================================

    if action_type == "open_url":
        target = (
            str(
                action.get(
                    "target",
                    ""
                )
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
                "Macro URL error:",
                error
            )

            return False

    print(
        f"Unknown macro action: {action_type}"
    )

    return False


# =========================================================
# RUN MACRO
# =========================================================

def run_macro(
    name
):
    macros = load_macros()

    name = (
        name
        .lower()
        .strip()
    )

    if name not in macros:
        return None

    actions = macros[
        name
    ]

    if not isinstance(
        actions,
        list
    ):
        return False

    success_count = 0

    for action in actions:
        try:
            if run_action(
                action
            ):
                success_count += 1

        except Exception as error:
            print(
                f"Macro action error in '{name}':",
                error
            )

    return success_count > 0


# =========================================================
# ADD / UPDATE MACRO
# =========================================================

def set_macro(
    name,
    actions
):
    name = (
        name
        .lower()
        .strip()
    )

    if not name:
        return False

    if not isinstance(
        actions,
        list
    ):
        return False

    macros = load_macros()

    macros[
        name
    ] = actions

    save_macros(
        macros
    )

    return True


# =========================================================
# DELETE MACRO
# =========================================================

def delete_macro(
    name
):
    macros = load_macros()

    name = (
        name
        .lower()
        .strip()
    )

    if name not in macros:
        return False

    del macros[
        name
    ]

    save_macros(
        macros
    )

    return True


# =========================================================
# LIST MACROS
# =========================================================

def list_macros():
    macros = load_macros()

    return sorted(
        macros.keys()
    )