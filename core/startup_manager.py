import json
import os
import sys
import winreg

from core.paths import user_file


STARTUP_SETTINGS_FILE = user_file(
    "startup_settings.json"
)

REGISTRY_PATH = (
    r"Software\Microsoft\Windows\CurrentVersion\Run"
)

REGISTRY_VALUE_NAME = "JARVIS"


DEFAULT_STARTUP_SETTINGS = {
    "start_with_windows": False,
    "start_minimized": True
}


# =========================================================
# SETTINGS
# =========================================================

def load_startup_settings():
    settings = DEFAULT_STARTUP_SETTINGS.copy()

    if not os.path.exists(
        STARTUP_SETTINGS_FILE
    ):
        return settings

    try:
        with open(
            STARTUP_SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            saved = json.load(
                file
            )

        if isinstance(
            saved,
            dict
        ):
            settings.update(
                saved
            )

    except Exception as error:
        print(
            "Startup settings load error:",
            error
        )

    return settings


def save_startup_settings(
    settings
):
    os.makedirs(
        os.path.dirname(
            STARTUP_SETTINGS_FILE
        ),
        exist_ok=True
    )

    with open(
        STARTUP_SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            settings,
            file,
            indent=4
        )


# =========================================================
# STARTUP COMMAND
# =========================================================

def get_startup_command(
    start_minimized=True
):
    arguments = []

    if start_minimized:
        arguments.append(
            "--minimized"
        )

    # =====================================================
    # PACKAGED JARVIS.EXE
    # =====================================================

    if getattr(
        sys,
        "frozen",
        False
    ):
        executable = os.path.abspath(
            sys.executable
        )

        command = (
            f'"{executable}"'
        )

    # =====================================================
    # DEVELOPMENT MODE
    # =====================================================

    else:
        python_executable = os.path.abspath(
            sys.executable
        )

        python_folder = os.path.dirname(
            python_executable
        )

        pythonw_executable = os.path.join(
            python_folder,
            "pythonw.exe"
        )

        if os.path.exists(
            pythonw_executable
        ):
            python_executable = pythonw_executable

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(
                    __file__
                )
            )
        )

        main_file = os.path.join(
            project_root,
            "main.py"
        )

        command = (
            f'"{python_executable}" '
            f'"{main_file}"'
        )

    if arguments:
        command += (
            " "
            + " ".join(
                arguments
            )
        )

    return command


# =========================================================
# WINDOWS REGISTRY
# =========================================================

def enable_windows_startup(
    start_minimized=True
):
    command = get_startup_command(
        start_minimized
    )

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        REGISTRY_PATH,
        0,
        winreg.KEY_SET_VALUE
    )

    try:
        winreg.SetValueEx(
            key,
            REGISTRY_VALUE_NAME,
            0,
            winreg.REG_SZ,
            command
        )

    finally:
        winreg.CloseKey(
            key
        )

    return command


def disable_windows_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )

    except FileNotFoundError:
        return

    try:
        try:
            winreg.DeleteValue(
                key,
                REGISTRY_VALUE_NAME
            )

        except FileNotFoundError:
            pass

    finally:
        winreg.CloseKey(
            key
        )


def get_registered_startup_command():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )

    except FileNotFoundError:
        return ""

    try:
        try:
            value, _ = winreg.QueryValueEx(
                key,
                REGISTRY_VALUE_NAME
            )

            return str(
                value
            )

        except FileNotFoundError:
            return ""

    finally:
        winreg.CloseKey(
            key
        )


def is_windows_startup_enabled():
    return bool(
        get_registered_startup_command()
    )


# =========================================================
# APPLY SETTINGS
# =========================================================

def apply_startup_settings(
    settings
):
    enabled = bool(
        settings.get(
            "start_with_windows",
            False
        )
    )

    minimized = bool(
        settings.get(
            "start_minimized",
            True
        )
    )

    save_startup_settings(
        settings
    )

    if enabled:
        return enable_windows_startup(
            minimized
        )

    disable_windows_startup()

    return ""