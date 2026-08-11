import json
import os

DETECTED_FILE = "data/apps_detected.json"
APP_FILE = "data/apps.json"


def load_json(path):
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print(f"Could not load {path}: {error}")
        return {}


def save_json(path, data):
    os.makedirs("data", exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def search_apps(search_term):
    detected = load_json(DETECTED_FILE)

    search_term = search_term.lower().strip()

    matches = {}

    for app_name, app_path in detected.items():
        if search_term in app_name.lower():
            matches[app_name] = app_path

    return matches


def assign_alias(alias, app_name):
    detected = load_json(DETECTED_FILE)
    apps = load_json(APP_FILE)

    alias = alias.lower().strip()
    app_name = app_name.lower().strip()

    if app_name not in detected:
        return False

    apps[alias] = detected[app_name]

    save_json(APP_FILE, apps)

    return True


def list_aliases():
    return load_json(APP_FILE)


def main():
    print("JARVIS App Alias Manager")
    print()

    while True:
        search_term = input(
            "Search for an app, or type 'exit': "
        ).strip()

        if search_term.lower() == "exit":
            break

        matches = search_apps(search_term)

        if not matches:
            print("No apps found.")
            print()
            continue

        match_list = list(matches.items())

        print()
        print("Matches:")
        print()

        for index, (name, path) in enumerate(match_list, start=1):
            print(f"{index}. {name}")
            print(f"   {path}")

        print()

        choice = input(
            "Enter the number of the app you want: "
        ).strip()

        try:
            choice = int(choice)

            if choice < 1 or choice > len(match_list):
                print("Invalid choice.")
                print()
                continue

        except ValueError:
            print("Please enter a number.")
            print()
            continue

        selected_name, selected_path = match_list[choice - 1]

        print()
        print(f"Selected: {selected_name}")
        print(selected_path)

        alias = input(
            "What should JARVIS call this app? "
        ).strip()

        if not alias:
            print("Alias cannot be empty.")
            print()
            continue

        if assign_alias(alias, selected_name):
            print()
            print(
                f"Saved alias '{alias}' -> {selected_name}"
            )
            print()

        else:
            print("Could not save alias.")
            print()


if __name__ == "__main__":
    main()