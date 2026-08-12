import json
import os
import shutil
import subprocess

from core.paths import user_file
from core.ai_mode import load_ai_settings


SETUP_FILE = user_file("setup_complete.json")


def is_setup_complete():
    if not os.path.exists(SETUP_FILE):
        return False

    try:
        with open(
            SETUP_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        return bool(
            data.get("complete", False)
        )

    except Exception:
        return False


def mark_setup_complete():
    os.makedirs(
        os.path.dirname(SETUP_FILE),
        exist_ok=True
    )

    with open(
        SETUP_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            {
                "complete": True
            },
            file,
            indent=4
        )


def reset_setup():
    if os.path.exists(SETUP_FILE):
        os.remove(SETUP_FILE)


def find_ollama():
    path = shutil.which("ollama")

    if path:
        return path

    possible_paths = [
        os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Ollama\ollama.exe"
        )
    ]

    for possible in possible_paths:
        if os.path.exists(possible):
            return possible

    return None


def ollama_installed():
    return find_ollama() is not None


def get_installed_models():
    ollama = find_ollama()

    if not ollama:
        return []

    try:
        result = subprocess.run(
            [
                ollama,
                "list"
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode != 0:
            return []

        lines = result.stdout.splitlines()

        models = []

        for line in lines[1:]:
            line = line.strip()

            if not line:
                continue

            model_name = line.split()[0]

            if model_name:
                models.append(model_name)

        return models

    except Exception as error:
        print(
            "Could not list Ollama models:",
            error
        )

        return []


def model_installed(model_name):
    installed = get_installed_models()

    return model_name in installed


def pull_model(model_name):
    ollama = find_ollama()

    if not ollama:
        return False, "Ollama is not installed."

    try:
        process = subprocess.run(
            [
                ollama,
                "pull",
                model_name
            ],
            text=True
        )

        if process.returncode == 0:
            return True, f"{model_name} installed."

        return False, f"Could not install {model_name}."

    except Exception as error:
        return False, str(error)


def get_required_models():
    settings = load_ai_settings()

    return [
        settings["normal_model"],
        settings["think_model"]
    ]