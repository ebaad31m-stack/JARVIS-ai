import os
import json

OUTPUT_FILE = "data/apps_detected.json"

BUILT_IN_APPS = {
    "file explorer": "explorer.exe",
    "settings": "ms-settings:",
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe"
}


SCAN_FOLDERS = [
    os.path.expandvars(r"%ProgramFiles%"),
    os.path.expandvars(r"%ProgramFiles(x86)%"),
    os.path.expandvars(r"%LOCALAPPDATA%"),
    os.path.expandvars(r"%APPDATA%"),
]


IGNORE_FOLDERS = {
    "windows",
    "system32",
    "winsxs",
    "packages",
    "cache",
    "temp",
    "logs",
    "node_modules",
}


def is_ignored(path):
    lowered = path.lower()

    for ignored in IGNORE_FOLDERS:
        if f"\\{ignored}\\" in lowered:
            return True

    return False


def scan_apps():
    detected = {}

    for base_folder in SCAN_FOLDERS:

        if not base_folder or not os.path.exists(base_folder):
            continue

        print(f"Scanning: {base_folder}")

        for root, dirs, files in os.walk(base_folder):

            if is_ignored(root):
                dirs[:] = []
                continue

            for file in files:

                if not file.lower().endswith(".exe"):
                    continue

                full_path = os.path.join(root, file)

                app_name = os.path.splitext(file)[0].lower()

                if app_name not in detected:
                    detected[app_name] = full_path

    for name, target in BUILT_IN_APPS.items():
        detected[name] = target

    return detected


def save_detected_apps(apps):
    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(apps, file, indent=4)

    print()
    print(f"Saved {len(apps)} detected apps to:")
    print(OUTPUT_FILE)


def main():
    apps = scan_apps()
    save_detected_apps(apps)


if __name__ == "__main__":
    main()