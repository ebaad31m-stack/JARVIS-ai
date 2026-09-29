import json
import os

from core.paths import user_file


PERSONALIZATION_FILE = user_file(
    "personalization.json"
)


DEFAULT_SETTINGS = {
    "assistant_name": "JARVIS",

    # Built-in openWakeWord model.
    "wake_model": "hey_jarvis",

    # Display name for the wake phrase.
    "wake_phrase": "Hey JARVIS",

    # Used only when wake_model == "custom".
    "custom_wake_model_path": "",

    "phrases": {
        "online": "",
        "listening": "I'm listening.",
        "one_moment": "One moment, sir.",
        "done": "Done, sir.",
        "sleep": "Going back to sleep.",
        "couldnt_generate": (
            "I couldn't generate the requested content, sir."
        ),
        "shutdown": "",
        "shutdown_cancelled": "Shutdown cancelled.",
        "email_sent": "Email sent, sir.",
        "email_cancelled": "Email cancelled, sir.",
    }
}


WAKE_MODELS = {
    "hey_jarvis": {
        "label": "Hey JARVIS",
        "phrase": "Hey JARVIS",
    },

    "alexa": {
        "label": "Alexa",
        "phrase": "Alexa",
    },

    "hey_mycroft": {
        "label": "Hey Mycroft",
        "phrase": "Hey Mycroft",
    },

    "hey_rhasspy": {
        "label": "Hey Rhasspy",
        "phrase": "Hey Rhasspy",
    },

    "timer": {
        "label": "Timer",
        "phrase": "Timer",
    },

    "weather": {
        "label": "Weather",
        "phrase": "Weather",
    },

    "custom": {
        "label": "Custom ONNX Model",
        "phrase": "Custom wake phrase",
    },
}


def _copy_defaults():
    return {
        "assistant_name":
            DEFAULT_SETTINGS["assistant_name"],

        "wake_model":
            DEFAULT_SETTINGS["wake_model"],

        "wake_phrase":
            DEFAULT_SETTINGS["wake_phrase"],

        "custom_wake_model_path":
            DEFAULT_SETTINGS[
                "custom_wake_model_path"
            ],

        "phrases":
            DEFAULT_SETTINGS["phrases"].copy(),
    }


def load_personalization():
    settings = _copy_defaults()

    if not os.path.exists(
        PERSONALIZATION_FILE
    ):
        return settings

    try:

        with open(
            PERSONALIZATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved = json.load(
                file
            )

        if not isinstance(
            saved,
            dict
        ):
            return settings

        for key in (
            "assistant_name",
            "wake_model",
            "wake_phrase",
            "custom_wake_model_path",
        ):

            if key in saved:

                settings[key] = (
                    saved[key]
                )

        saved_phrases = saved.get(
            "phrases"
        )

        if isinstance(
            saved_phrases,
            dict
        ):

            settings["phrases"].update(
                saved_phrases
            )

    except Exception as error:

        print(
            "Personalization load error:",
            error
        )

    return settings


def save_personalization(
    settings
):
    os.makedirs(
        os.path.dirname(
            PERSONALIZATION_FILE
        ),
        exist_ok=True
    )

    clean = _copy_defaults()

    clean["assistant_name"] = (
        str(
            settings.get(
                "assistant_name",
                "JARVIS"
            )
        )
        .strip()
        or "JARVIS"
    )

    clean["wake_model"] = (
        str(
            settings.get(
                "wake_model",
                "hey_jarvis"
            )
        )
        .strip()
        .lower()
    )

    if clean["wake_model"] not in WAKE_MODELS:

        clean["wake_model"] = "hey_jarvis"

    clean["wake_phrase"] = (
        str(
            settings.get(
                "wake_phrase",
                ""
            )
        )
        .strip()
    )

    if not clean["wake_phrase"]:

        clean["wake_phrase"] = (
            WAKE_MODELS[
                clean["wake_model"]
            ]["phrase"]
        )

    clean["custom_wake_model_path"] = (
        str(
            settings.get(
                "custom_wake_model_path",
                ""
            )
        )
        .strip()
    )

    phrases = (
        settings.get(
            "phrases",
            {}
        )
    )

    if isinstance(
        phrases,
        dict
    ):

        for key in clean["phrases"]:

            if key in phrases:

                clean["phrases"][key] = (
                    str(
                        phrases[key]
                        or ""
                    )
                    .strip()
                )

    with open(
        PERSONALIZATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            clean,
            file,
            indent=4,
            ensure_ascii=False
        )

    return clean


def get_assistant_name():
    return (
        load_personalization()
        .get(
            "assistant_name",
            "JARVIS"
        )
        .strip()
        or "JARVIS"
    )


def get_wake_model():
    model = (
        load_personalization()
        .get(
            "wake_model",
            "hey_jarvis"
        )
    )

    model = str(
        model
    ).strip().lower()

    if model not in WAKE_MODELS:

        return "hey_jarvis"

    return model


def get_wake_phrase():
    settings = load_personalization()

    phrase = str(
        settings.get(
            "wake_phrase",
            ""
        )
    ).strip()

    if phrase:

        return phrase

    model = get_wake_model()

    return WAKE_MODELS[
        model
    ]["phrase"]


def get_custom_wake_model_path():
    return (
        load_personalization()
        .get(
            "custom_wake_model_path",
            ""
        )
        .strip()
    )


def get_phrase(
    key
):
    settings = load_personalization()

    phrases = settings.get(
        "phrases",
        {}
    )

    custom = str(
        phrases.get(
            key,
            ""
        )
        or ""
    ).strip()

    name = get_assistant_name()

    dynamic_defaults = {
        "online":
            f"{name} is online.",

        "shutdown":
            f"{name} shutting down.",
    }

    if custom:

        return custom

    return dynamic_defaults.get(
        key,
        DEFAULT_SETTINGS[
            "phrases"
        ].get(
            key,
            ""
        )
    )


# ============================================================
# SPEECH PHRASE OVERRIDES
# ============================================================

PHRASE_KEYS = {
    "JARVIS is online.": "online",
    "I'm listening.": "listening",
    "One moment, sir.": "one_moment",
    "Done, sir.": "done",
    "Going back to sleep.": "sleep",
    "I couldn't generate the requested content, sir.":
        "couldnt_generate",
    "JARVIS shutting down.": "shutdown",
    "Shutdown cancelled.": "shutdown_cancelled",
    "Email sent, sir.": "email_sent",
    "Email cancelled, sir.": "email_cancelled",
}


def apply_phrase_override(
    text
):
    text = str(
        text
        or ""
    )

    stripped = text.strip()

    key = PHRASE_KEYS.get(
        stripped
    )

    if key is None:

        return text

    replacement = get_phrase(
        key
    )

    if not replacement:

        return text

    return replacement