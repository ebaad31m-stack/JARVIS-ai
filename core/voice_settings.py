import json
import os

from core.paths import user_file


VOICE_SETTINGS_FILE = user_file(
    "voice_settings.json"
)


BRIAN_VOICE_ID = "nPczCjzI2devNBz1zQrb"


DEFAULT_VOICE_SETTINGS = {
    "provider": "piper",

    "piper_voice": "en_US-lessac-medium.onnx",

    "elevenlabs_api_key": "",
    "elevenlabs_voice_name": "Brian",
    "elevenlabs_voice_id": BRIAN_VOICE_ID,
    "elevenlabs_model": "eleven_flash_v2_5"
}


def load_voice_settings():
    if not os.path.exists(
        VOICE_SETTINGS_FILE
    ):
        return DEFAULT_VOICE_SETTINGS.copy()

    try:
        with open(
            VOICE_SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            saved = json.load(file)

        settings = DEFAULT_VOICE_SETTINGS.copy()

        settings.update(
            saved
        )

        return settings

    except Exception as error:
        print(
            "Voice settings load error:",
            error
        )

        return DEFAULT_VOICE_SETTINGS.copy()


def save_voice_settings(settings):
    os.makedirs(
        os.path.dirname(
            VOICE_SETTINGS_FILE
        ),
        exist_ok=True
    )

    current = DEFAULT_VOICE_SETTINGS.copy()

    current.update(
        settings
    )

    with open(
        VOICE_SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            current,
            file,
            indent=4
        )


def reset_voice_settings():
    save_voice_settings(
        DEFAULT_VOICE_SETTINGS.copy()
    )