import json
import os

from core.paths import user_file


AI_SETTINGS_FILE = user_file(
    "ai_settings.json"
)

DEFAULT_AI_SETTINGS = {
    "normal_model": "qwen2.5:1.5b",
    "think_model": "gemma3:4b",
    "coding_model": "qwen2.5-coder:7b",
    "temperature": 0.7,
}


_current_mode = "normal"


def load_ai_settings():
    if not os.path.exists(
        AI_SETTINGS_FILE
    ):
        return DEFAULT_AI_SETTINGS.copy()

    try:
        with open(
            AI_SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            saved = json.load(
                file
            )

        return {
            "normal_model": str(
                saved.get(
                    "normal_model",
                    DEFAULT_AI_SETTINGS["normal_model"]
                )
            ).strip() or DEFAULT_AI_SETTINGS["normal_model"],
            "think_model": str(
                saved.get(
                    "think_model",
                    DEFAULT_AI_SETTINGS["think_model"]
                )
            ).strip() or DEFAULT_AI_SETTINGS["think_model"],
            "coding_model": str(
                saved.get(
                    "coding_model",
                    DEFAULT_AI_SETTINGS["coding_model"]
                )
            ).strip() or DEFAULT_AI_SETTINGS["coding_model"],
            "temperature": saved.get(
                "temperature",
                DEFAULT_AI_SETTINGS["temperature"]
            ),
        }

    except Exception as error:
        print(
            "AI settings load error:",
            error
        )

        return DEFAULT_AI_SETTINGS.copy()


def save_ai_settings(settings):
    incoming = settings if isinstance(settings, dict) else {}
    current = load_ai_settings()

    merged = {
        "normal_model": str(
            incoming.get(
                "normal_model",
                current["normal_model"]
            )
        ).strip() or DEFAULT_AI_SETTINGS["normal_model"],
        "think_model": str(
            incoming.get(
                "think_model",
                current["think_model"]
            )
        ).strip() or DEFAULT_AI_SETTINGS["think_model"],
        "coding_model": str(
            incoming.get(
                "coding_model",
                current.get(
                    "coding_model",
                    DEFAULT_AI_SETTINGS["coding_model"]
                )
            )
        ).strip() or DEFAULT_AI_SETTINGS["coding_model"],
        "temperature": incoming.get(
            "temperature",
            current.get(
                "temperature",
                DEFAULT_AI_SETTINGS["temperature"]
            )
        ),
    }

    os.makedirs(
        os.path.dirname(
            AI_SETTINGS_FILE
        ),
        exist_ok=True
    )

    with open(
        AI_SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            merged,
            file,
            indent=4
        )


def set_ai_mode(mode):
    global _current_mode

    mode = str(mode).lower().strip()

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


def get_coding_model():
    settings = load_ai_settings()
    return settings.get(
        "coding_model",
        DEFAULT_AI_SETTINGS["coding_model"]
    )


def get_temperature():
    settings = load_ai_settings()

    try:
        return float(
            settings["temperature"]
        )
    except Exception:
        return 0.7
