import ctypes
import json
import os

from ctypes import wintypes

from PIL import ImageGrab

from core.paths import user_file


SCREEN_SETTINGS_FILE = user_file(
    "screen_settings.json"
)


DEFAULT_SCREEN_SETTINGS = {
    "monitor": "all"
}


# =========================================================
# WINDOWS STRUCTURES
# =========================================================

class RECT(
    ctypes.Structure
):
    _fields_ = [
        (
            "left",
            wintypes.LONG,
        ),
        (
            "top",
            wintypes.LONG,
        ),
        (
            "right",
            wintypes.LONG,
        ),
        (
            "bottom",
            wintypes.LONG,
        ),
    ]


class MONITORINFOEXW(
    ctypes.Structure
):
    _fields_ = [
        (
            "cbSize",
            wintypes.DWORD,
        ),
        (
            "rcMonitor",
            RECT,
        ),
        (
            "rcWork",
            RECT,
        ),
        (
            "dwFlags",
            wintypes.DWORD,
        ),
        (
            "szDevice",
            wintypes.WCHAR * 32,
        ),
    ]


class DISPLAY_DEVICEW(
    ctypes.Structure
):
    _fields_ = [
        (
            "cb",
            wintypes.DWORD,
        ),
        (
            "DeviceName",
            wintypes.WCHAR * 32,
        ),
        (
            "DeviceString",
            wintypes.WCHAR * 128,
        ),
        (
            "StateFlags",
            wintypes.DWORD,
        ),
        (
            "DeviceID",
            wintypes.WCHAR * 128,
        ),
        (
            "DeviceKey",
            wintypes.WCHAR * 128,
        ),
    ]


# =========================================================
# GET FRIENDLY DISPLAY NAME
# =========================================================

def get_monitor_friendly_name(
    display_device_name
):
    if os.name != "nt":
        return display_device_name

    try:
        user32 = ctypes.windll.user32

        display_device = DISPLAY_DEVICEW()

        display_device.cb = (
            ctypes.sizeof(
                DISPLAY_DEVICEW
            )
        )

        success = user32.EnumDisplayDevicesW(
            display_device_name,
            0,
            ctypes.byref(
                display_device
            ),
            0,
        )

        if success:
            name = (
                str(
                    display_device.DeviceString
                )
                .strip()
            )

            if name:
                return name

    except Exception as error:
        print(
            "Monitor friendly-name error:",
            error,
        )

    return display_device_name


# =========================================================
# MONITOR DETECTION
# =========================================================

def get_monitors():
    monitors = []

    if os.name != "nt":
        return monitors

    try:
        user32 = ctypes.windll.user32

        monitor_enum_proc = (
            ctypes.WINFUNCTYPE(
                wintypes.BOOL,
                wintypes.HMONITOR,
                wintypes.HDC,
                ctypes.POINTER(
                    RECT
                ),
                wintypes.LPARAM,
            )
        )

        def callback(
            monitor_handle,
            hdc,
            rect_pointer,
            data,
        ):
            monitor_info = (
                MONITORINFOEXW()
            )

            monitor_info.cbSize = (
                ctypes.sizeof(
                    MONITORINFOEXW
                )
            )

            success = (
                user32.GetMonitorInfoW(
                    monitor_handle,
                    ctypes.byref(
                        monitor_info
                    ),
                )
            )

            if not success:
                return True

            rect = (
                monitor_info.rcMonitor
            )

            left = int(
                rect.left
            )

            top = int(
                rect.top
            )

            right = int(
                rect.right
            )

            bottom = int(
                rect.bottom
            )

            device_name = (
                str(
                    monitor_info.szDevice
                )
                .strip()
            )

            friendly_name = (
                get_monitor_friendly_name(
                    device_name
                )
            )

            monitors.append(
                {
                    "id":
                        device_name,

                    "name":
                        friendly_name,

                    "device":
                        device_name,

                    "x":
                        left,

                    "y":
                        top,

                    "width":
                        right - left,

                    "height":
                        bottom - top,

                    "primary":
                        bool(
                            monitor_info.dwFlags
                            & 1
                        ),
                }
            )

            return True

        callback_function = (
            monitor_enum_proc(
                callback
            )
        )

        user32.EnumDisplayMonitors(
            None,
            None,
            callback_function,
            0,
        )

    except Exception as error:
        print(
            "Monitor detection error:",
            error,
        )

    # Put primary first for consistency.
    monitors.sort(
        key=lambda monitor: (
            not monitor.get(
                "primary",
                False,
            ),
            monitor.get(
                "x",
                0,
            ),
            monitor.get(
                "y",
                0,
            ),
        )
    )

    return monitors


# =========================================================
# LOAD SETTINGS
# =========================================================

def load_screen_settings():
    settings = (
        DEFAULT_SCREEN_SETTINGS.copy()
    )

    if not os.path.exists(
        SCREEN_SETTINGS_FILE
    ):
        return settings

    try:
        with open(
            SCREEN_SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            saved = json.load(
                file
            )

        if isinstance(
            saved,
            dict,
        ):
            settings.update(
                saved
            )

    except Exception as error:
        print(
            "Screen settings load error:",
            error,
        )

    return settings


# =========================================================
# SAVE SETTINGS
# =========================================================

def save_screen_settings(
    settings
):
    current = (
        DEFAULT_SCREEN_SETTINGS.copy()
    )

    if isinstance(
        settings,
        dict,
    ):
        current.update(
            settings
        )

    folder = os.path.dirname(
        SCREEN_SETTINGS_FILE
    )

    if folder:
        os.makedirs(
            folder,
            exist_ok=True,
        )

    try:
        with open(
            SCREEN_SETTINGS_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                current,
                file,
                indent=4,
            )

        return current

    except Exception as error:
        print(
            "Screen settings save error:",
            error,
        )

        return current


# =========================================================
# SELECTED MONITOR ID
# =========================================================

def get_selected_monitor():
    settings = (
        load_screen_settings()
    )

    return str(
        settings.get(
            "monitor",
            "all",
        )
    )


# =========================================================
# FIND SELECTED MONITOR
# =========================================================

def get_selected_monitor_info():
    monitors = get_monitors()

    selection = (
        get_selected_monitor()
    )

    if (
        selection == "all"
        or not monitors
    ):
        return None

    # New format:
    # \\.\DISPLAY1
    for monitor in monitors:
        if monitor.get(
            "id"
        ) == selection:
            return monitor

    # Compatibility with the old numeric
    # "1", "2", "3" setting.
    try:
        old_index = (
            int(
                selection
            )
            - 1
        )

        if (
            0 <= old_index
            < len(
                monitors
            )
        ):
            return monitors[
                old_index
            ]

    except Exception:
        pass

    return monitors[
        0
    ]


# =========================================================
# CAPTURE GEOMETRY
# =========================================================

def get_capture_geometry():
    monitors = get_monitors()

    selection = (
        get_selected_monitor()
    )

    if not monitors:
        return {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
            "all": True,
            "name": "All Monitors",
        }

    # =====================================================
    # ALL MONITORS
    # =====================================================

    if selection == "all":
        left = min(
            monitor[
                "x"
            ]
            for monitor in monitors
        )

        top = min(
            monitor[
                "y"
            ]
            for monitor in monitors
        )

        right = max(
            monitor[
                "x"
            ]
            + monitor[
                "width"
            ]
            for monitor in monitors
        )

        bottom = max(
            monitor[
                "y"
            ]
            + monitor[
                "height"
            ]
            for monitor in monitors
        )

        return {
            "x":
                left,

            "y":
                top,

            "width":
                right - left,

            "height":
                bottom - top,

            "all":
                True,

            "name":
                "All Monitors",
        }

    # =====================================================
    # SPECIFIC MONITOR
    # =====================================================

    monitor = (
        get_selected_monitor_info()
    )

    if monitor is None:
        monitor = monitors[
            0
        ]

    geometry = (
        monitor.copy()
    )

    geometry[
        "all"
    ] = False

    return geometry


# =========================================================
# CAPTURE SELECTED SCREEN
# =========================================================

def capture_selected_screen():
    geometry = (
        get_capture_geometry()
    )

    try:
        if geometry.get(
            "all",
            False,
        ):
            image = ImageGrab.grab(
                all_screens=True
            )

        else:
            left = geometry[
                "x"
            ]

            top = geometry[
                "y"
            ]

            right = (
                left
                + geometry[
                    "width"
                ]
            )

            bottom = (
                top
                + geometry[
                    "height"
                ]
            )

            image = ImageGrab.grab(
                bbox=(
                    left,
                    top,
                    right,
                    bottom,
                ),
                all_screens=True,
            )

        return (
            image,
            geometry,
        )

    except Exception as error:
        print(
            "Selected screen capture error:",
            error,
        )

        return (
            None,
            geometry,
        )