import json
import os
import subprocess
import webbrowser

import psutil


from core.paths import user_file

APP_FILE = user_file("apps.json")


def load_apps():
    if not os.path.exists(APP_FILE):
        return {}

    try:
        with open(APP_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print("App launcher load error:", error)
        return {}


def launch_app(name):
    apps = load_apps()

    name = name.lower().strip()

    if name not in apps:
        return None

    target = apps[name]

    try:
        # Website
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)

        # Windows URI
        elif target.startswith("ms-"):
            os.startfile(target)

        # Normal app
        else:
            subprocess.Popen([target])

        return True

    except Exception as error:
        print(f"App launcher error for '{name}':", error)
        return False


def close_app(name):
    apps = load_apps()

    name = name.lower().strip()

    if name not in apps:
        return None

    target = apps[name]

    # We cannot reliably close a specific website/tab yet.
    if target.startswith("http://") or target.startswith("https://"):
        return False

    # Windows URI apps need their own closing logic later.
    if target.startswith("ms-"):
        return False

    try:
        process_name = os.path.basename(target).lower()

        found = False

        for process in psutil.process_iter(
            ["pid", "name", "exe"]
        ):
            try:
                running_name = (
                    process.info["name"] or ""
                ).lower()

                running_exe = (
                    process.info["exe"] or ""
                ).lower()

                target_lower = target.lower()

                if (
                    running_name == process_name
                    or running_exe == target_lower
                ):
                    process.terminate()
                    found = True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

        return found

    except Exception as error:
        print(f"App close error for '{name}':", error)
        return False