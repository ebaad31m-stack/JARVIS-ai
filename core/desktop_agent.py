import ctypes
import time

import psutil
import pyautogui
import pyperclip


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.03


user32 = ctypes.windll.user32


def get_active_window_info():
    hwnd = user32.GetForegroundWindow()

    title_length = user32.GetWindowTextLengthW(hwnd)

    buffer = ctypes.create_unicode_buffer(
        title_length + 1
    )

    user32.GetWindowTextW(
        hwnd,
        buffer,
        title_length + 1
    )

    pid = ctypes.c_ulong()

    user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(pid)
    )

    process_name = ""

    try:
        process_name = psutil.Process(
            pid.value
        ).name()

    except Exception:
        pass

    return {
        "hwnd": hwnd,
        "title": buffer.value.strip(),
        "process": process_name
    }


def get_active_window_context():
    info = get_active_window_info()

    title = (
        info["title"]
        or "Unknown window"
    )

    process = (
        info["process"]
        or "Unknown process"
    )

    return (
        f"Active application: {process}\n"
        f"Window title: {title}"
    )


def copy_selected_text(
    wait_seconds=0.35
):
    try:
        previous = pyperclip.paste()

    except Exception:
        previous = ""

    marker = "__JARVIS_NO_SELECTION__"

    try:
        pyperclip.copy(
            marker
        )

        time.sleep(
            0.05
        )

        pyautogui.hotkey(
            "ctrl",
            "c"
        )

        time.sleep(
            wait_seconds
        )

        selected = pyperclip.paste()

    except Exception as error:
        print(
            "Selection copy error:",
            error
        )

        return None

    finally:
        try:
            pyperclip.copy(
                previous
            )

        except Exception:
            pass

    if (
        not selected
        or selected == marker
    ):
        return None

    return selected


def paste_text(
    text,
    wait_seconds=0.20
):
    if text is None:
        return False

    text = str(
        text
    )

    if not text:
        return False

    try:
        previous = pyperclip.paste()

    except Exception:
        previous = ""

    try:
        pyperclip.copy(
            text
        )

        time.sleep(
            0.05
        )

        pyautogui.hotkey(
            "ctrl",
            "v"
        )

        time.sleep(
            wait_seconds
        )

        return True

    except pyautogui.FailSafeException:
        print(
            "Desktop agent stopped by "
            "PyAutoGUI fail-safe."
        )

        return False

    except Exception as error:
        print(
            "Desktop paste error:",
            error
        )

        return False

    finally:
        try:
            pyperclip.copy(
                previous
            )

        except Exception:
            pass