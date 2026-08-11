import json
import os


AI_SETTINGS_FILE = "data/ai_settings.json"

DEFAULT_AI_SETTINGS = {
    "normal_model": "qwen2.5:1.5b",
    "think_model": "gemma3:4b",
    "temperature": 0.7
}

_current_mode = "normal"


def load_ai_settings():
    if not os.path.exists(AI_SETTINGS_FILE):
        return DEFAULT_AI_SETTINGS.copy()

    try:
        with open(
            AI_SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            saved = json.load(file)

        return {
            "normal_model": saved.get(
                "normal_model",
                DEFAULT_AI_SETTINGS["normal_model"]
            ),
            "think_model": saved.get(
                "think_model",
                DEFAULT_AI_SETTINGS["think_model"]
            ),
            "temperature": saved.get(
                "temperature",
                DEFAULT_AI_SETTINGS["temperature"]
            )
        }

    except Exception as error:
        print("AI settings load error:", error)
        return DEFAULT_AI_SETTINGS.copy()


def save_ai_settings(settings):
    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        AI_SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            settings,
            file,
            indent=4
        )


def set_ai_mode(mode):
    global _current_mode

    mode = mode.lower().strip()

    if mode == "think":
        _current_mode = "think"
    else:
        _current_mode = "normal"


def get_ai_mode():
    return _current_mode


def get_ai_mode_label():
    if _current_mode == "think":
        return "THINK MODE"

    return "NORMAL MODE"


def get_current_model():
    settings = load_ai_settings()

    if _current_mode == "think":
        return settings["think_model"]

    return settings["normal_model"]


def get_temperature():
    settings = load_ai_settings()

    try:
        return float(
            settings["temperature"]
        )

    except Exception:
        return 0.7