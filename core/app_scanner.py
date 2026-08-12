import json
import os

from core.paths import user_file


OUTPUT_FILE = user_file(
    "apps_detected.json"
)


BUILT_IN_APPS = {
    "File Explorer": "explorer.exe",
    "Settings": "ms-settings:",
    "Calculator": "calc.exe",
    "Notepad": "notepad.exe",
    "Task Manager": "taskmgr.exe",
    "Control Panel": "control.exe"
}


SKIP_NAMES = {
    "uninstall.exe",
    "unins000.exe",
    "update.exe",
    "updater.exe"
}


def get_scan_roots():
    roots = []

    environment_paths = [
        os.environ.get(
            "ProgramFiles"
        ),
        os.environ.get(
            "ProgramFiles(x86)"
        ),
        os.environ.get(
            "LOCALAPPDATA"
        ),
        os.environ.get(
            "APPDATA"
        )
    ]

    for path in environment_paths:
        if (
            path
            and os.path.exists(path)
            and path not in roots
        ):
            roots.append(
                path
            )

    return roots


def scan_apps():
    detected = BUILT_IN_APPS.copy()

    for root in get_scan_roots():
        print(
            "Scanning:",
            root
        )

        try:
            for current_root, dirs, files in os.walk(
                root
            ):
                for filename in files:
                    if not filename.lower().endswith(
                        ".exe"
                    ):
                        continue

                    if filename.lower() in SKIP_NAMES:
                        continue

                    full_path = os.path.join(
                        current_root,
                        filename
                    )

                    friendly_name = os.path.splitext(
                        filename
                    )[0]

                    key = friendly_name

                    number = 2

                    while (
                        key in detected
                        and detected[key] != full_path
                    ):
                        key = (
                            f"{friendly_name} "
                            f"({number})"
                        )

                        number += 1

                    detected[
                        key
                    ] = full_path

        except Exception as error:
            print(
                "App scan error:",
                root,
                error
            )

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            detected,
            file,
            indent=4
        )

    print(
        f"Saved {len(detected)} "
        f"detected apps to:"
    )

    print(
        OUTPUT_FILE
    )

    return detected


if __name__ == "__main__":
    scan_apps()